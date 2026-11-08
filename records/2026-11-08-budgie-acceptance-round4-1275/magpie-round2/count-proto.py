import glob,re,sys,collections
pat={'source_create':r'-> ext_foreign_toplevel_image_capture_source_manager_v1#\d+\.create_source','source_destroy':r'-> ext_image_capture_source_v1#\d+\.destroy',
'session_create':r'-> ext_image_copy_capture_manager_v1#\d+\.create_session','session_destroy':r'-> ext_image_copy_capture_session_v1#\d+\.destroy',
'frame_create':r'-> ext_image_copy_capture_session_v1#\d+\.create_frame','frame_destroy':r'-> ext_image_copy_capture_frame_v1#\d+\.destroy','frame_ready':r' ext_image_copy_capture_frame_v1#\d+\.ready','frame_failed':r' ext_image_copy_capture_frame_v1#\d+\.failed',
'shm_buffer_create':r'-> wl_shm_pool#\d+\.create_buffer','buffer_destroy':r'-> wl_buffer#\d+\.destroy','disconnect_ok':r'x'}
for f in sorted(glob.glob(sys.argv[1]+'/helper-*.wl')):
    c=collections.Counter()
    for l in open(f,errors='replace'):
        for k,p in pat.items():
            if re.search(p,l): c[k]+=1
    print(f.rsplit('/',1)[1],dict(c))
