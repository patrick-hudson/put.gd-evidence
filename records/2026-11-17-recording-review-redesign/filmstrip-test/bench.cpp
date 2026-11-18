#include <QImage>
extern "C" {
#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libavutil/imgutils.h>
#include <libswscale/swscale.h>
}
#include <algorithm>
#include <chrono>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <memory>
#include <random>
#include <stdexcept>
#include <string_view>
#include <sys/resource.h>
#include <vector>

using Clock = std::chrono::steady_clock;
using Frame = std::unique_ptr<AVFrame, decltype([](AVFrame* f) { av_frame_free(&f); })>;

void checked(int code, const char* what) {
    if (code >= 0) return;
    char reason[AV_ERROR_MAX_STRING_SIZE]{};
    av_strerror(code, reason, sizeof reason);
    throw std::runtime_error(std::string(what) + ": " + reason);
}

struct Decoder {
    AVFormatContext* format = nullptr;
    AVCodecContext* codec = nullptr;
    AVPacket* packet = av_packet_alloc();
    Frame frame{av_frame_alloc()};
    int stream = -1;
    int64_t origin = 0;
    AVRational timebase{};
    const char* file;
    const bool nonkey;
    bool pending = false;
    bool draining = false;
    unsigned packets = 0;
    unsigned frames = 0;
    unsigned keys = 0;
    unsigned bframes = 0;
    int64_t lastKey = AV_NOPTS_VALUE;
    int64_t maxKeyGap = 0;

    Decoder(const char* path, bool skip) : file(path), nonkey(skip) { open(); }
    void open() {
        checked(avformat_open_input(&format, file, nullptr, nullptr), "open");
        checked(avformat_find_stream_info(format, nullptr), "stream info");
        const AVCodec* impl = nullptr;
        stream = av_find_best_stream(format, AVMEDIA_TYPE_VIDEO, -1, -1, &impl, 0);
        checked(stream, "video stream");
        const AVStream* track = format->streams[stream];
        codec = avcodec_alloc_context3(impl);
        checked(avcodec_parameters_to_context(codec, track->codecpar), "codec parameters");
        codec->thread_count = 0;
        codec->thread_type = FF_THREAD_FRAME | FF_THREAD_SLICE;
        if (nonkey) codec->skip_frame = AVDISCARD_NONKEY;
        checked(avcodec_open2(codec, impl, nullptr), "decoder");
        timebase = track->time_base;
        origin = track->start_time == AV_NOPTS_VALUE ? 0 : track->start_time;
    }
    ~Decoder() {
        av_packet_free(&packet);
        avcodec_free_context(&codec);
        avformat_close_input(&format);
    }

    int readVideo() {
        int status;
        while ((status = av_read_frame(format, packet)) >= 0 && packet->stream_index != stream) {
            av_packet_unref(packet);
        }
        return status;
    }

    int64_t seek(int64_t us) {
        const int64_t target = origin + av_rescale_q(us, {1, 1000000}, timebase);
        av_frame_unref(frame.get());
        av_packet_unref(packet);
        draining = pending = false;
        int status = av_seek_frame(format, stream, target, AVSEEK_FLAG_BACKWARD);
        avcodec_flush_buffers(codec);
        if (status >= 0 && readVideo() >= 0 && packet->pts != AV_NOPTS_VALUE &&
            packet->pts <= target && (packet->flags & AV_PKT_FLAG_KEY)) {
            pending = true;
        } else {
            // Same fallback as Input::seekTo when the first Matroska cue overshoots.
            av_packet_unref(packet);
            avcodec_free_context(&codec);
            avformat_close_input(&format);
            open();
        }
        return target;
    }

    // A submits a single packet and drains frame-thread delay. C and exact
    // seeks keep feeding packets until EOF or until the caller has its frame.
    bool next(bool onePacket = false) {
        while (true) {
            av_frame_unref(frame.get());
            const int status = avcodec_receive_frame(codec, frame.get());
            if (status == AVERROR_EOF) return false;
            if (status != AVERROR(EAGAIN)) {
                checked(status, "receive");
                ++frames;
                if (frame->flags & AV_FRAME_FLAG_KEY) {
                    ++keys;
                    const auto pts = frame->best_effort_timestamp;
                    if (lastKey != AV_NOPTS_VALUE) maxKeyGap = std::max(maxKeyGap, pts - lastKey);
                    lastKey = pts;
                }
                if (frame->pict_type == AV_PICTURE_TYPE_B) ++bframes;
                return true;
            }
            if (draining) throw std::runtime_error("decoder needs input after drain");
            const int input = onePacket ? AVERROR_EOF : pending ? 0 : readVideo();
            if (input == AVERROR_EOF) {
                checked(avcodec_send_packet(codec, nullptr), "drain");
                draining = true;
                continue;
            }
            checked(input, "read video packet");
            submit();
        }
    }
    void submit() {
        checked(avcodec_send_packet(codec, packet), "send");
        av_packet_unref(packet);
        pending = false;
        ++packets;
    }
    void key() {
        if (!pending) checked(readVideo(), "first key packet");
        if (!(packet->flags & AV_PKT_FLAG_KEY)) throw std::runtime_error("seek did not land on a key packet");
        submit();
        if (!next(true) || !(frame->flags & AV_FRAME_FLAG_KEY)) throw std::runtime_error("key frame unavailable");
    }
    void exact(int64_t target) {
        while (next()) {
            if (frame->best_effort_timestamp >= target) return;
        }
        throw std::runtime_error("no frame at or after the target");
    }
};

QImage scale(const AVFrame& src, int w, int h, bool fullRgb) {
    Frame rgb{av_frame_alloc()};
    rgb->format = AV_PIX_FMT_BGRA;
    rgb->width = fullRgb ? src.width : w;
    rgb->height = fullRgb ? src.height : h;
    checked(av_frame_get_buffer(rgb.get(), 64), "RGB buffer");
    std::unique_ptr<SwsContext, decltype(&sws_freeContext)> sws(
        sws_getContext(src.width, src.height, AVPixelFormat(src.format),
                       rgb->width, rgb->height, AV_PIX_FMT_BGRA, SWS_BILINEAR,
                       nullptr, nullptr, nullptr), sws_freeContext);
    if (!sws) throw std::runtime_error("scaler unavailable");
    checked(sws_scale(sws.get(), src.data, src.linesize, 0, src.height, rgb->data, rgb->linesize), "scale");
    QImage image(rgb->width, rgb->height, QImage::Format_RGB32);
    for (int y = 0; y < rgb->height; ++y) {
        std::memcpy(image.scanLine(y), rgb->data[0] + size_t(y) * rgb->linesize[0], size_t(rgb->width) * 4);
    }
    return fullRgb ? image.scaled(w, h, Qt::IgnoreAspectRatio, Qt::SmoothTransformation) : image;
}

double ms(Clock::duration d) { return std::chrono::duration<double, std::milli>(d).count(); }
double secs(timeval t) { return t.tv_sec + t.tv_usec * 1e-6; }

int main(int argc, char** argv) try {
    if (argc != 5) throw std::runtime_error("usage: bench CLIP A|An|B|C|Cn|D|Dopen N SEED");
    const char* clip = argv[1];
    const std::string_view mode = argv[2];
    const int n = std::stoi(argv[3]);
    const bool key = mode == "A" || mode == "An";
    const bool pass = mode == "C" || mode == "Cn";
    const bool skim = mode == "D" || mode == "Dopen";
    const auto begin = Clock::now();
    auto decoder = std::make_unique<Decoder>(clip, mode == "An" || mode == "Cn");
    const auto openEnd = Clock::now();
    const int64_t duration = decoder->format->duration;
    const int threads = decoder->codec->thread_count;
    const int threadType = decoder->codec->active_thread_type;
    if (duration <= 20000) throw std::runtime_error("clip too short");
    // Skim times must precede the last frame. Tile times match --motion's
    // bin centers, with the first and last tile prioritized.
    const int64_t last = duration - 20000;
    std::vector<int64_t> targets;
    if (skim) {
        std::mt19937 rng(std::stoul(argv[4]));
        std::uniform_int_distribution<int64_t> at(0, last);
        for (int i = 0; i < n; ++i) targets.push_back(at(rng));
    } else if (!pass) {
        const auto center = [=](int i) { return duration * (2 * i + 1) / (2 * n); };
        targets = {center(0), center(n - 1)};
        for (int i = 1; i < n - 1; ++i) targets.push_back(center(i));
    }
    std::vector<double> calls;
    double firstTwo = 0;
    unsigned pixel = 0;
    unsigned packets = 0;
    unsigned frames = 0;
    if (pass) {
        while (decoder->next()) {}
        packets = decoder->packets;
        frames = decoder->frames;
    } else {
        for (auto time : targets) {
            const auto started = Clock::now();
            if (mode == "Dopen") decoder = std::make_unique<Decoder>(clip, false);
            const unsigned initialPackets = decoder->packets;
            const unsigned initialFrames = decoder->frames;
            const auto target = decoder->seek(time);
            if (key) decoder->key();
            else decoder->exact(target);
            auto image = scale(*decoder->frame, skim ? 1010 : 128, skim ? 568 : 72, !key);
            pixel ^= image.pixel(0, 0);
            const auto done = Clock::now();
            calls.push_back(ms(done - started));
            if (calls.size() == 2) firstTwo = ms(done - begin);
            packets += decoder->packets - initialPackets;
            frames += decoder->frames - initialFrames;
        }
    }
    const int keys = decoder->keys;
    const int bframes = decoder->bframes;
    const auto keyGapUs = av_rescale_q(decoder->maxKeyGap, decoder->timebase, {1, 1000000});
    decoder.reset();
    const double wall = ms(Clock::now() - begin);
    rusage used{};
    getrusage(RUSAGE_SELF, &used);
    std::cout << std::fixed << std::setprecision(3)
              << "{\"mode\":\"" << mode << "\",\"n\":" << n << ",\"wall_ms\":" << wall
              << ",\"open_ms\":" << ms(openEnd - begin) << ",\"first_two_ms\":" << firstTwo
              << ",\"cpu_seconds\":" << secs(used.ru_utime) + secs(used.ru_stime)
              << ",\"rss_kib\":" << used.ru_maxrss << ",\"packets\":" << packets
              << ",\"frames\":" << frames << ",\"keys\":" << keys << ",\"bframes\":" << bframes
              << ",\"max_key_gap_us\":" << keyGapUs
              << ",\"threads\":" << threads << ",\"thread_type\":" << threadType
              << ",\"duration_us\":" << duration << ",\"pixel\":" << pixel << ",\"calls_ms\":[";
    for (size_t i = 0; i < calls.size(); ++i) std::cout << (i ? "," : "") << calls[i];
    std::cout << "]}\n";
    return 0;
} catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
}
