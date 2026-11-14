add_executable(link_notice_harness ${CMAKE_SOURCE_DIR}/../harness/link_notice.cpp)
target_include_directories(link_notice_harness PRIVATE ${CMAKE_SOURCE_DIR}/tests)
target_link_libraries(link_notice_harness PRIVATE putgd_tray Qt6::Test Qt6::DBus)
