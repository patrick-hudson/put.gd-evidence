// syncprobe OUT: wl_display.sync round trips on an independent client, as fast as they return with 4 ms between them. Logs each round trip over 15 ms as "realtime ms".
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <wayland-client.h>
static int done;
static void cb(void* d, struct wl_callback* c, uint32_t t) { (void)t; done = 1; wl_callback_destroy(c); }
static const struct wl_callback_listener l = { cb };
static double now(void) { struct timespec t; clock_gettime(CLOCK_REALTIME, &t); return t.tv_sec + t.tv_nsec / 1e9; }
int main(int argc, char** argv) {
 struct wl_display* d = wl_display_connect(0); if (!d) return 1;
 FILE* f = fopen(argv[1], "w"); setvbuf(f, 0, _IOLBF, 0);
 unsigned long n = 0;
 for (;;) {
  double a = now(); done = 0; struct wl_callback* c = wl_display_sync(d); wl_callback_add_listener(c, &l, 0);
  wl_display_flush(d);
  while (!done) if (wl_display_dispatch(d) < 0) return 2;
  double b = now(); n++;
  if ((b - a) * 1000 > 15) fprintf(f, "%.3f %.1f\n", a, (b - a) * 1000);
  if (n % 2000 == 0) fprintf(f, "# alive %lu %.3f\n", n, b);
  usleep(4000);
 }
}
