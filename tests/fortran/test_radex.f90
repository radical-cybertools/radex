program test_radex_fortran
  !! Simple test to verify Fortran bindings compile and link correctly
  use radex
  use iso_c_binding
  implicit none

  type(c_ptr) :: client
  integer :: stat
  integer(c_int32_t) :: i32_value
  real(c_double) :: f64_value
  logical :: exists

  print *, "Testing RaDex Fortran Binding Module..."
  print *, "Attempting to create Dragon client..."

  client = radex_client_dragon_create()
  print *, "Client created successfully"

  ! Test put_int32
  print *, ""
  print *, "Testing client_put_int32..."
  call client_put_int32(client, "fortran_test_int32", int(42, c_int32_t), stat)
  if (stat /= RADEX_OK) then
    print *, "ERROR: put_int32 failed with status", stat
    stop 1
  end if
  print *, "SUCCESS: put_int32 worked"

  ! Test get_int32
  print *, "Testing client_get_int32..."
  call client_get_int32(client, "fortran_test_int32", i32_value, stat)
  if (stat /= RADEX_OK) then
    print *, "ERROR: get_int32 failed with status", stat
    stop 1
  end if
  if (i32_value /= 42) then
    print *, "ERROR: get_int32 returned wrong value:", i32_value
    stop 1
  end if
  print *, "SUCCESS: get_int32 returned", i32_value

  ! Test put_float64
  print *, ""
  print *, "Testing client_put_float64..."
  call client_put_float64(client, "fortran_test_float64", 3.14159_c_double, stat)
  if (stat /= RADEX_OK) then
    print *, "ERROR: put_float64 failed with status", stat
    stop 1
  end if
  print *, "SUCCESS: put_float64 worked"

  ! Test get_float64
  print *, "Testing client_get_float64..."
  call client_get_float64(client, "fortran_test_float64", f64_value, stat)
  if (stat /= RADEX_OK) then
    print *, "ERROR: get_float64 failed with status", stat
    stop 1
  end if
  if (f64_value /= 3.14159_c_double) then
    print *, "ERROR: get_float64 returned wrong value:", f64_value
    stop 1
  end if
  print *, "SUCCESS: get_float64 returned", f64_value

  ! Test contains
  print *, ""
  print *, "Testing client_contains..."
  call client_contains(client, "fortran_test_int32", exists, stat)
  if (stat /= RADEX_OK .and. stat /= 1) then
    print *, "ERROR: contains failed with status", stat
    stop 1
  end if
  if (.not. exists) then
    print *, "ERROR: contains should return true for existing key"
    stop 1
  end if
  print *, "SUCCESS: contains returned true"

  ! Cleanup
  print *, ""
  print *, "Cleaning up..."
  stat = radex_client_destroy(client)
  if (stat /= RADEX_OK) then
    print *, "ERROR: destroy failed with status", stat
    stop 1
  end if
  print *, "SUCCESS: client destroyed"

  print *, ""
  print *, "All Fortran binding tests passed!"

end program test_radex_fortran
