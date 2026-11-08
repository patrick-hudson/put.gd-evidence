// Minimal ext-image-copy-capture client (no put.gd code): open capture sessions
// on one toplevel in a loop, capture frames for N seconds in each, destroy
// everything, print frames and content changes per session.
// mincap <title> <sessions> <seconds> [gap_ms]
#define _GNU_SOURCE
#include <fcntl.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>
#include <wayland-client.h>
#include "ext-foreign-toplevel-list-v1-client-protocol.h"
#include "ext-image-capture-source-v1-client-protocol.h"
#include "ext-image-copy-capture-v1-client-protocol.h"
static struct wl_shm* shm; static struct ext_foreign_toplevel_list_v1* list;
static struct ext_foreign_toplevel_image_capture_source_manager_v1* srcm; static struct ext_image_copy_capture_manager_v1* cap;
static struct ext_foreign_toplevel_handle_v1* target; static const char* want;
static int w,h,cons; static int ready_ev,failed_ev,fail_reason;
static double now(){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+t.tv_nsec/1e9;}
static void h_closed(void*d,struct ext_foreign_toplevel_handle_v1*x){}
static void h_done(void*d,struct ext_foreign_toplevel_handle_v1*x){}
static void h_title(void*d,struct ext_foreign_toplevel_handle_v1*x,const char*t){if(!strcmp(t,want))target=x;}
static void h_app(void*d,struct ext_foreign_toplevel_handle_v1*x,const char*t){}
static void h_id(void*d,struct ext_foreign_toplevel_handle_v1*x,const char*t){}
static const struct ext_foreign_toplevel_handle_v1_listener hl={h_closed,h_done,h_title,h_app,h_id};
static void l_top(void*d,struct ext_foreign_toplevel_list_v1*l,struct ext_foreign_toplevel_handle_v1*x){ext_foreign_toplevel_handle_v1_add_listener(x,&hl,0);}
static void l_fin(void*d,struct ext_foreign_toplevel_list_v1*l){}
static const struct ext_foreign_toplevel_list_v1_listener ll={l_top,l_fin};
static void g(void*d,struct wl_registry*r,uint32_t n,const char*i,uint32_t v){
 if(!strcmp(i,"wl_shm"))shm=wl_registry_bind(r,n,&wl_shm_interface,1);
 else if(!strcmp(i,ext_foreign_toplevel_list_v1_interface.name)){list=wl_registry_bind(r,n,&ext_foreign_toplevel_list_v1_interface,1);ext_foreign_toplevel_list_v1_add_listener(list,&ll,0);}
 else if(!strcmp(i,ext_foreign_toplevel_image_capture_source_manager_v1_interface.name))srcm=wl_registry_bind(r,n,&ext_foreign_toplevel_image_capture_source_manager_v1_interface,1);
 else if(!strcmp(i,ext_image_copy_capture_manager_v1_interface.name))cap=wl_registry_bind(r,n,&ext_image_copy_capture_manager_v1_interface,1);
}
static void gr(void*d,struct wl_registry*r,uint32_t n){}
static const struct wl_registry_listener rl={g,gr};
static void s_size(void*d,struct ext_image_copy_capture_session_v1*s,uint32_t a,uint32_t b){w=a;h=b;}
static void s_fmt(void*d,struct ext_image_copy_capture_session_v1*s,uint32_t f){}
static void s_dev(void*d,struct ext_image_copy_capture_session_v1*s,struct wl_array*a){}
static void s_dma(void*d,struct ext_image_copy_capture_session_v1*s,uint32_t f,struct wl_array*a){}
static void s_done(void*d,struct ext_image_copy_capture_session_v1*s){cons=1;}
static void s_stop(void*d,struct ext_image_copy_capture_session_v1*s){failed_ev=1;fail_reason=-1;}
static const struct ext_image_copy_capture_session_v1_listener sl={s_size,s_fmt,s_dev,s_dma,s_done,s_stop};
static void f_tr(void*d,struct ext_image_copy_capture_frame_v1*f,uint32_t t){}
static void f_dm(void*d,struct ext_image_copy_capture_frame_v1*f,int32_t a,int32_t b,int32_t c,int32_t e){}
static void f_pt(void*d,struct ext_image_copy_capture_frame_v1*f,uint32_t a,uint32_t b,uint32_t c){}
static void f_rd(void*d,struct ext_image_copy_capture_frame_v1*f){ready_ev=1;}
static void f_fl(void*d,struct ext_image_copy_capture_frame_v1*f,uint32_t r){failed_ev=1;fail_reason=(int)r;}
static const struct ext_image_copy_capture_frame_v1_listener fl={f_tr,f_dm,f_pt,f_rd,f_fl};
static int pump(struct wl_display*dp,double until){ // dispatch until an event flag or the deadline; 0 on timeout
 while(!ready_ev&&!failed_ev){
  if(now()>=until)return 0;
  while(wl_display_prepare_read(dp)!=0)wl_display_dispatch_pending(dp);
  wl_display_flush(dp);
  struct pollfd p={wl_display_get_fd(dp),POLLIN,0};int ms=(int)((until-now())*1000)+1;
  if(poll(&p,1,ms)>0)wl_display_read_events(dp);else wl_display_cancel_read(dp);
  wl_display_dispatch_pending(dp);
 }
 return 1;
}
int main(int c,char**v){
 if(c<4){fprintf(stderr,"mincap title sessions seconds [gap_ms]\n");return 2;}
 want=v[1];int sessions=atoi(v[2]);double secs=atof(v[3]);int gap=c>4?atoi(v[4]):0;
 struct wl_display*dp=wl_display_connect(0);if(!dp){perror("connect");return 1;}
 struct wl_registry*r=wl_display_get_registry(dp);wl_registry_add_listener(r,&rl,0);
 wl_display_roundtrip(dp);wl_display_roundtrip(dp);wl_display_roundtrip(dp);
 if(!target||!cap||!srcm||!shm){fprintf(stderr,"missing: target=%p cap=%p srcm=%p shm=%p\n",target,cap,srcm,shm);return 1;}
 for(int i=0;i<sessions;i++){
  cons=0;w=h=0;
  struct ext_image_capture_source_v1*src=ext_foreign_toplevel_image_capture_source_manager_v1_create_source(srcm,target);
  struct ext_image_copy_capture_session_v1*s=ext_image_copy_capture_manager_v1_create_session(cap,src,EXT_IMAGE_COPY_CAPTURE_MANAGER_V1_OPTIONS_PAINT_CURSORS);
  ext_image_copy_capture_session_v1_add_listener(s,&sl,0);
  while(!cons)if(wl_display_roundtrip(dp)<0)return 1;
  size_t sz=(size_t)w*h*4;int fd=memfd_create("mc",MFD_CLOEXEC);ftruncate(fd,sz);unsigned char*mem=mmap(0,sz,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);
  unsigned char*prev=malloc(sz);int havePrev=0;
  struct wl_shm_pool*pool=wl_shm_create_pool(shm,fd,sz);struct wl_buffer*b=wl_shm_pool_create_buffer(pool,0,w,h,w*4,WL_SHM_FORMAT_ARGB8888);wl_shm_pool_destroy(pool);close(fd);
  int frames=0,changed=0,fails=0;double start=now(),end=start+secs;double firstAt=-1;
  while(now()<end){
   ready_ev=failed_ev=0;
   struct ext_image_copy_capture_frame_v1*f=ext_image_copy_capture_session_v1_create_frame(s);
   ext_image_copy_capture_frame_v1_add_listener(f,&fl,0);
   ext_image_copy_capture_frame_v1_attach_buffer(f,b);ext_image_copy_capture_frame_v1_damage_buffer(f,0,0,w,h);ext_image_copy_capture_frame_v1_capture(f);
   wl_display_flush(dp);
   int got=pump(dp,end);
   if(got&&ready_ev){frames++;if(firstAt<0)firstAt=now()-start;if(havePrev&&memcmp(prev,mem,sz))changed++;memcpy(prev,mem,sz);havePrev=1;}
   else if(got&&failed_ev){fails++;}
   ext_image_copy_capture_frame_v1_destroy(f);
   if(fails>5)break;
  }
  wl_buffer_destroy(b);munmap(mem,sz);free(prev);ext_image_copy_capture_session_v1_destroy(s);ext_image_capture_source_v1_destroy(src);wl_display_roundtrip(dp);
  printf("session %d size %dx%d frames %d changed %d fails %d first_frame_ms %.0f\n",i,w,h,frames,changed,fails,firstAt*1000);fflush(stdout);
  if(gap)usleep(gap*1000);
 }
 ext_foreign_toplevel_list_v1_stop(list);wl_display_roundtrip(dp);wl_display_disconnect(dp);return 0;
}
