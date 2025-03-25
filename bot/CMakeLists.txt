cmake_minimum_required(VERSION 3.8)
project(bot)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)

# Install launch, URDF, and params files
install(
  DIRECTORY launch urdf params worlds config
  DESTINATION share/${PROJECT_NAME}
)

# Install Python script
install(
  PROGRAMS scripts/square_movement.py
  DESTINATION lib/${PROJECT_NAME}
)

# Testing (optional)
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
