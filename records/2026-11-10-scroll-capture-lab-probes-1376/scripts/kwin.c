#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <wayland-client.h>
#include "fake.h"
#include "cast.h"
static struct org_kde_kwin_fake_input *fake;
static struct zkde_screencast_unstable_v1 *cast;
static int ready=0;
static void global(void *d, struct wl_registry *r,uint32_t n,const char *i,uint32_t v){
 if(!strcmp(i,"org_kde_kwin_fake_input"))fake=wl_registry_bind(r,n,&org_kde_kwin_fake_input_interface,v<4?v:4);
 if(!strcmp(i,"zkde_screencast_unstable_v1"))cast=wl_registry_bind(r,n,&zkde_screencast_unstable_v1_interface,v<5?v:5);
}
static void removed(void*d,struct wl_registry*r,uint32_t n){}
static void closed(void*d,struct zkde_screencast_stream_unstable_v1*s){fprintf(stderr,"closed\n");}
static void created(void*d,struct zkde_screencast_stream_unstable_v1*s,uint32_t n){printf("%u\n",n);fflush(stdout);ready=1;}
static void failed(void*d,struct zkde_screencast_stream_unstable_v1*s,const char*e){fprintf(stderr,"failed %s\n",e);exit(2);}
int main(int argc,char**argv){
 struct wl_display*d=wl_display_connect(NULL);if(!d)return 2;struct wl_registry*r=wl_display_get_registry(d);static const struct wl_registry_listener rl={global,removed};wl_registry_add_listener(r,&rl,0);wl_display_roundtrip(d);fprintf(stderr,"fake=%d cast=%d\n",!!fake,!!cast);if(!fake||!cast)return 3;
 org_kde_kwin_fake_input_authenticate(fake,"Scroll probe","Standalone wheel probe");
 double scale=argc>1?atof(argv[1]):1; struct zkde_screencast_stream_unstable_v1*s=zkde_screencast_unstable_v1_stream_region(cast,0,150/scale,1800/scale,600/scale,wl_fixed_from_double(scale),1);static const struct zkde_screencast_stream_unstable_v1_listener sl={closed,created,failed};zkde_screencast_stream_unstable_v1_add_listener(s,&sl,0);while(!ready&&wl_display_dispatch(d)>=0){}
 getchar();org_kde_kwin_fake_input_pointer_motion_absolute(fake,wl_fixed_from_double(500/scale),wl_fixed_from_double(400/scale));wl_display_roundtrip(d);usleep(200000);org_kde_kwin_fake_input_axis(fake,0,wl_fixed_from_double(15));wl_display_roundtrip(d);fprintf(stderr,"axis15 sent\n");getchar();zkde_screencast_stream_unstable_v1_close(s);wl_display_roundtrip(d);wl_display_disconnect(d);
}
