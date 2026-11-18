#include <QColor>
#include <QGuiApplication>
#include <QImage>
#include <QPainter>
#include <gst/app/gstappsrc.h>
#include <iostream>
#include <cmath>

int main(int argc, char** argv) {
    if (argc != 5) {
        std::cerr << "usage: fixture WIDTH HEIGHT THREADS OUTPUT\n";
        return 2;
    }
    int width = std::stoi(argv[1]);
    int height = std::stoi(argv[2]);
    int threads = std::stoi(argv[3]);
    const char* path = argv[4];
    QGuiApplication app(argc, argv);
    gst_init(nullptr, nullptr);
    const std::string pipeline = std::string(
        "appsrc name=source format=time block=true max-buffers=3 max-bytes=0 "
        "! videoconvert n-threads=") + std::to_string(std::min(4, threads)) +
        " ! video/x-raw,format=I420 ! queue max-size-buffers=3 max-size-bytes=0 max-size-time=0 "
        "! x264enc speed-preset=" + (width == 3840 ? "ultrafast bitrate=20000" : "superfast bitrate=12441") +
        " key-int-max=120 bframes=0 threads=" + std::to_string(threads) +
        " sliced-threads=false rc-lookahead=10 sync-lookahead=0 "
        "! h264parse ! matroskamux ! filesink name=output";
    GError* error = nullptr;
    GstElement* graph = gst_parse_launch(pipeline.c_str(), &error);
    if (error || !graph) {
        std::cerr << (error ? error->message : "pipeline unavailable") << '\n';
        return 1;
    }
    auto* source = GST_APP_SRC(gst_bin_get_by_name(GST_BIN(graph), "source"));
    auto* output = gst_bin_get_by_name(GST_BIN(graph), "output");
    g_object_set(output, "location", path, nullptr);
    gst_object_unref(output);
    auto* caps = gst_caps_new_simple("video/x-raw", "format", G_TYPE_STRING, "BGRx",
        "width", G_TYPE_INT, width, "height", G_TYPE_INT, height,
        "framerate", GST_TYPE_FRACTION, 60, 1, nullptr);
    gst_app_src_set_caps(source, caps);
    gst_caps_unref(caps);
    gst_element_set_state(graph, GST_STATE_PLAYING);

    // Two versions of a long browser page. Rasterized once at the target size
    // and repainted with a fresh scroll offset every frame.
    const qreal scale = width / 1920.0;
    QImage pages[2];
    const QColor accent[] = {QColor("#2566a6"), QColor("#257f64")};
    const QString headings[] = {"Deployment guide", "Incident handbook"};
    for (int page = 0; page < 2; ++page) {
        pages[page] = QImage(int(1570 * scale), int(4200 * scale), QImage::Format_RGB32);
        pages[page].fill(QColor("#f8fafc"));
        QPainter p(&pages[page]);
        p.scale(scale, scale);
        for (int section = 0; section < 12; ++section) {
            const int y = section * 350;
            p.fillRect(35, y + 16, 1495, 320, QColor("#ffffff"));
            p.fillRect(35, y + 16, 6, 320, accent[page]);
            p.setFont(QFont("DejaVu Sans", 19, QFont::Bold));
            p.setPen(accent[page]);
            p.drawText(65, y + 57, QString("%1  /  Section %2").arg(headings[page]).arg(section + 1));
            p.setFont(QFont("DejaVu Sans", 12));
            p.setPen(QColor("#27384b"));
            for (int line = 0; line < 9; ++line) {
                p.drawText(65, y + 87 + 23 * line,
                    QString("Step %1. Review the staging log, confirm the service status, and record the result in the change ticket.").arg(section * 9 + line + 1));
            }
            p.fillRect(1045, y + 68, 450, 217, QColor("#e6edf4"));
            p.setPen(accent[page]);
            for (int col = 0; col < 15; ++col) {
                const int bar = 28 + ((col * 33 + section * 51 + page * 17) % 156);
                p.fillRect(1063 + col * 28, y + 268 - bar, 18, bar, accent[page]);
            }
        }
    }

    bool ok = true;
    auto* pool = gst_buffer_pool_new();
    auto* poolConfig = gst_buffer_pool_get_config(pool);
    gst_buffer_pool_config_set_params(poolConfig, nullptr, guint(width * height * 4), 4, 8);
    if (!gst_buffer_pool_set_config(pool, poolConfig) || !gst_buffer_pool_set_active(pool, TRUE)) return 1;
    for (int frame = 0; frame < 10800 && ok; ++frame) {
        GstBuffer* buffer = nullptr;
        if (gst_buffer_pool_acquire_buffer(pool, &buffer, nullptr) != GST_FLOW_OK) return 1;
        GstMapInfo map{};
        if (!gst_buffer_map(buffer, &map, GST_MAP_WRITE)) return 1;
        {
            QImage img(map.data, width, height, width * 4, QImage::Format_RGB32);
            QPainter p(&img);
            p.scale(scale, scale);
            const int page = (frame / 720) % 2;
            const int scroll = int(3000 * (0.5 - 0.5 * std::cos(frame * 0.003)));
            p.drawImage(QRect(350, 104, 1570, 940), pages[page],
                        QRect(0, int(scroll * scale), int(1570 * scale), int(940 * scale)));
            p.fillRect(0, 0, 1920, 104, QColor("#dce4ed"));
            p.fillRect(0, 104, 350, 976, QColor("#243447"));
            p.fillRect(350, 1044, 1570, 36, QColor("#243447"));
            p.fillRect(35, 38, 1840, 40, Qt::white);
            p.setFont(QFont("DejaVu Sans", 13));
            p.setPen(QColor("#243447"));
            p.drawText(60, 64, "workspace.example / engineering / " + headings[page]);
            p.drawText(45, 26, "Workspace     Documentation     Issues     Activity");
            p.setPen(Qt::white);
            for (int i = 0; i < 16; ++i) p.drawText(32, 156 + i * 41, QString("Engineering notes  /  %1").arg(i + 1));
            p.drawText(372, 1070, QString("Documentation workspace   |   %1 s   |   %2").arg(frame / 60).arg(headings[page]));

            if ((frame / 330) % 5 == 3) {
                p.fillRect(875, 468, 865, 464, QColor("#17212c"));
                p.fillRect(875, 468, 865, 40, QColor("#3b4c62"));
                p.drawText(897, 495, "Terminal  •  staging");
                p.setFont(QFont("DejaVu Sans Mono", 12));
                p.setPen(QColor("#b6edc5"));
                for (int i = 0; i < 13; ++i) p.drawText(904, 540 + 26 * i,
                    QString("[service %1] check %2: healthy").arg(i + 1).arg(frame / 6 - 13 + i));
            }
            const qreal x = 965 + 690 * std::sin(frame * 0.014);
            const qreal y = 532 + 340 * std::cos(frame * 0.020);
            p.setPen(QPen(Qt::black, 2));
            p.setBrush(Qt::white);
            p.drawPolygon(QPolygonF{{x,y}, {x+2,y+24}, {x+8,y+16}, {x+16,y+15}});
        }
        gst_buffer_unmap(buffer, &map);
        GST_BUFFER_PTS(buffer) = gst_util_uint64_scale(frame, GST_SECOND, 60);
        GST_BUFFER_DURATION(buffer) = gst_util_uint64_scale(frame + 1, GST_SECOND, 60) - GST_BUFFER_PTS(buffer);
        ok = gst_app_src_push_buffer(source, buffer) == GST_FLOW_OK;
        if ((frame + 1) % 1800 == 0) std::cerr << width << ' ' << frame + 1 << "/10800\n";
    }
    gst_app_src_end_of_stream(source);
    GstBus* bus = gst_element_get_bus(graph);
    GstMessage* message = gst_bus_timed_pop_filtered(bus, GST_CLOCK_TIME_NONE,
        GstMessageType(GST_MESSAGE_ERROR | GST_MESSAGE_EOS));
    if (GST_MESSAGE_TYPE(message) == GST_MESSAGE_ERROR) {
        gst_message_parse_error(message, &error, nullptr);
        std::cerr << error->message << '\n';
        ok = false;
    }
    gst_message_unref(message);
    gst_object_unref(bus);
    gst_element_set_state(graph, GST_STATE_NULL);
    gst_buffer_pool_set_active(pool, FALSE);
    gst_object_unref(pool);
    gst_object_unref(source);
    gst_object_unref(graph);
    return ok ? 0 : 1;
}
