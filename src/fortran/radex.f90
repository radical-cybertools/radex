module radex
  !! Fortran 2003+ binding module for RaDex C interface
  !! Uses iso_c_binding for C interoperability via bind(C)
  use iso_c_binding
  implicit none

  ! Error codes (must match radex/errno.h)
  integer(c_int), parameter :: RADEX_OK = 0
  integer(c_int), parameter :: RADEX_ERR_KEY_NOT_FOUND = 1
  integer(c_int), parameter :: RADEX_ERR_TIMEOUT = 2
  integer(c_int), parameter :: RADEX_ERR_TYPE_MISMATCH = 3
  integer(c_int), parameter :: RADEX_ERR_RANK_MISMATCH = 4
  integer(c_int), parameter :: RADEX_ERR_DTYPE_MISMATCH = 5
  integer(c_int), parameter :: RADEX_ERR_METADATA = 6
  integer(c_int), parameter :: RADEX_ERR_BACKEND_UNAVAILABLE = 7
  integer(c_int), parameter :: RADEX_ERR_UNKNOWN = 99

  private
  public :: RADEX_OK, RADEX_ERR_KEY_NOT_FOUND, RADEX_ERR_TIMEOUT
  public :: RADEX_ERR_TYPE_MISMATCH, RADEX_ERR_RANK_MISMATCH, RADEX_ERR_DTYPE_MISMATCH
  public :: RADEX_ERR_METADATA, RADEX_ERR_BACKEND_UNAVAILABLE, RADEX_ERR_UNKNOWN
  public :: radex_client_dragon_create, radex_client_smartredis_create, radex_client_destroy
  public :: radex_incoming_handle_create, radex_incoming_handle_destroy
  public :: radex_outgoing_handle_create, radex_outgoing_handle_destroy
  public :: radex_client_put_int32, radex_client_get_int32
  public :: radex_client_put_int64, radex_client_get_int64
  public :: radex_client_put_float32, radex_client_get_float32
  public :: radex_client_put_float64, radex_client_get_float64
  public :: radex_client_put_tensor_int32, radex_client_get_tensor_int32
  public :: radex_client_put_tensor_int64, radex_client_get_tensor_int64
  public :: radex_client_put_tensor_float32, radex_client_get_tensor_float32
  public :: radex_client_put_tensor_float64, radex_client_get_tensor_float64
  public :: radex_client_wait_for_int32, radex_client_wait_for_int64
  public :: radex_client_wait_for_float32, radex_client_wait_for_float64
  public :: radex_client_wait_for_tensor_int32, radex_client_wait_for_tensor_int64
  public :: radex_client_wait_for_tensor_float32, radex_client_wait_for_tensor_float64
  public :: radex_client_contains
  public :: client_put_int32, client_get_int32
  public :: client_put_int64, client_get_int64
  public :: client_put_float32, client_get_float32
  public :: client_put_float64, client_get_float64
  public :: client_contains

  ! =========================================================================
  ! C Function Interface Blocks (bind(C))
  ! =========================================================================

  interface

    ! Client lifecycle
    function radex_client_dragon_create() bind(C, name="radex_client_dragon_create")
      use iso_c_binding
      type(c_ptr) :: radex_client_dragon_create
    end function

    function radex_client_smartredis_create() bind(C, name="radex_client_smartredis_create")
      use iso_c_binding
      type(c_ptr) :: radex_client_smartredis_create
    end function

    integer(c_int) function radex_client_destroy(client) bind(C, name="radex_client_destroy")
      use iso_c_binding
      type(c_ptr), value :: client
    end function

    ! Handle lifecycle
    function radex_incoming_handle_create(key) bind(C, name="radex_incoming_handle_create")
      use iso_c_binding
      character(c_char), intent(in) :: key(*)
      type(c_ptr) :: radex_incoming_handle_create
    end function

    subroutine radex_incoming_handle_destroy(handle) bind(C, name="radex_incoming_handle_destroy")
      use iso_c_binding
      type(c_ptr), value :: handle
    end subroutine

    function radex_outgoing_handle_create(key) bind(C, name="radex_outgoing_handle_create")
      use iso_c_binding
      character(c_char), intent(in) :: key(*)
      type(c_ptr) :: radex_outgoing_handle_create
    end function

    subroutine radex_outgoing_handle_destroy(handle) bind(C, name="radex_outgoing_handle_destroy")
      use iso_c_binding
      type(c_ptr), value :: handle
    end subroutine

    ! put_int32
    integer(c_int) function radex_client_put_int32(client, handle, value) &
        bind(C, name="radex_client_put_int32")
      use iso_c_binding
      type(c_ptr), value :: client
      type(c_ptr), value :: handle
      integer(c_int32_t), value :: value
    end function

    ! get_int32
    integer(c_int) function radex_client_get_int32(client, handle, out_value) &
        bind(C, name="radex_client_get_int32")
      use iso_c_binding
      type(c_ptr), value :: client
      type(c_ptr), value :: handle
      integer(c_int32_t), intent(out) :: out_value
    end function

    ! put_int64
    integer(c_int) function radex_client_put_int64(client, handle, value) &
        bind(C, name="radex_client_put_int64")
      use iso_c_binding
      type(c_ptr), value :: client
      type(c_ptr), value :: handle
      integer(c_int64_t), value :: value
    end function

    ! get_int64
    integer(c_int) function radex_client_get_int64(client, handle, out_value) &
        bind(C, name="radex_client_get_int64")
      use iso_c_binding
      type(c_ptr), value :: client
      type(c_ptr), value :: handle
      integer(c_int64_t), intent(out) :: out_value
    end function

    ! put_float32
    integer(c_int) function radex_client_put_float32(client, handle, value) &
        bind(C, name="radex_client_put_float32")
      use iso_c_binding
      type(c_ptr), value :: client
      type(c_ptr), value :: handle
      real(c_float), value :: value
    end function

    ! get_float32
    integer(c_int) function radex_client_get_float32(client, handle, out_value) &
        bind(C, name="radex_client_get_float32")
      use iso_c_binding
      type(c_ptr), value :: client
      type(c_ptr), value :: handle
      real(c_float), intent(out) :: out_value
    end function

    ! put_float64
    integer(c_int) function radex_client_put_float64(client, handle, value) &
        bind(C, name="radex_client_put_float64")
      use iso_c_binding
      type(c_ptr), value :: client
      type(c_ptr), value :: handle
      real(c_double), value :: value
    end function

    ! get_float64
    integer(c_int) function radex_client_get_float64(client, handle, out_value) &
        bind(C, name="radex_client_get_float64")
      use iso_c_binding
      type(c_ptr), value :: client
      type(c_ptr), value :: handle
      real(c_double), intent(out) :: out_value
    end function

    ! put_tensor_int32
    integer(c_int) function radex_client_put_tensor_int32(client, key, key_len, data, rank, dims) &
        bind(C, name="radex_client_put_tensor_int32")
      use iso_c_binding
      type(c_ptr), value :: client
      character(c_char), intent(in) :: key(*)
      integer(c_int), value :: key_len
      integer(c_int32_t), intent(in) :: data(*)
      integer(c_int), value :: rank
      integer(c_int), intent(in) :: dims(*)
    end function

    ! get_tensor_int32
    integer(c_int) function radex_client_get_tensor_int32(client, key, key_len, &
        out_data, max_elements, out_rank, out_dims, max_dims) &
        bind(C, name="radex_client_get_tensor_int32")
      use iso_c_binding
      type(c_ptr), value :: client
      character(c_char), intent(in) :: key(*)
      integer(c_int), value :: key_len
      integer(c_int32_t), intent(out) :: out_data(*)
      integer(c_int), value :: max_elements
      integer(c_int), intent(out) :: out_rank
      integer(c_int), intent(out) :: out_dims(*)
      integer(c_int), value :: max_dims
    end function

    ! put_tensor_int64
    integer(c_int) function radex_client_put_tensor_int64(client, key, key_len, data, rank, dims) &
        bind(C, name="radex_client_put_tensor_int64")
      use iso_c_binding
      type(c_ptr), value :: client
      character(c_char), intent(in) :: key(*)
      integer(c_int), value :: key_len
      integer(c_int64_t), intent(in) :: data(*)
      integer(c_int), value :: rank
      integer(c_int), intent(in) :: dims(*)
    end function

    ! get_tensor_int64
    integer(c_int) function radex_client_get_tensor_int64(client, key, key_len, &
        out_data, max_elements, out_rank, out_dims, max_dims) &
        bind(C, name="radex_client_get_tensor_int64")
      use iso_c_binding
      type(c_ptr), value :: client
      character(c_char), intent(in) :: key(*)
      integer(c_int), value :: key_len
      integer(c_int64_t), intent(out) :: out_data(*)
      integer(c_int), value :: max_elements
      integer(c_int), intent(out) :: out_rank
      integer(c_int), intent(out) :: out_dims(*)
      integer(c_int), value :: max_dims
    end function

    ! put_tensor_float32
    integer(c_int) function radex_client_put_tensor_float32(client, key, key_len, data, rank, dims) &
        bind(C, name="radex_client_put_tensor_float32")
      use iso_c_binding
      type(c_ptr), value :: client
      character(c_char), intent(in) :: key(*)
      integer(c_int), value :: key_len
      real(c_float), intent(in) :: data(*)
      integer(c_int), value :: rank
      integer(c_int), intent(in) :: dims(*)
    end function

    ! get_tensor_float32
    integer(c_int) function radex_client_get_tensor_float32(client, key, key_len, &
        out_data, max_elements, out_rank, out_dims, max_dims) &
        bind(C, name="radex_client_get_tensor_float32")
      use iso_c_binding
      type(c_ptr), value :: client
      character(c_char), intent(in) :: key(*)
      integer(c_int), value :: key_len
      real(c_float), intent(out) :: out_data(*)
      integer(c_int), value :: max_elements
      integer(c_int), intent(out) :: out_rank
      integer(c_int), intent(out) :: out_dims(*)
      integer(c_int), value :: max_dims
    end function

    ! put_tensor_float64
    integer(c_int) function radex_client_put_tensor_float64(client, key, key_len, data, rank, dims) &
        bind(C, name="radex_client_put_tensor_float64")
      use iso_c_binding
      type(c_ptr), value :: client
      character(c_char), intent(in) :: key(*)
      integer(c_int), value :: key_len
      real(c_double), intent(in) :: data(*)
      integer(c_int), value :: rank
      integer(c_int), intent(in) :: dims(*)
    end function

    ! get_tensor_float64
    integer(c_int) function radex_client_get_tensor_float64(client, key, key_len, &
        out_data, max_elements, out_rank, out_dims, max_dims) &
        bind(C, name="radex_client_get_tensor_float64")
      use iso_c_binding
      type(c_ptr), value :: client
      character(c_char), intent(in) :: key(*)
      integer(c_int), value :: key_len
      real(c_double), intent(out) :: out_data(*)
      integer(c_int), value :: max_elements
      integer(c_int), intent(out) :: out_rank
      integer(c_int), intent(out) :: out_dims(*)
      integer(c_int), value :: max_dims
    end function

    ! contains
    integer(c_int) function radex_client_contains(client, handle) &
        bind(C, name="radex_client_contains")
      use iso_c_binding
      type(c_ptr), value :: client
      type(c_ptr), value :: handle
    end function

    ! wait_for_int32
    integer(c_int) function radex_client_wait_for_int32(client, handle, out_value, timeout_ms) &
        bind(C, name="radex_client_wait_for_int32")
      use iso_c_binding
      type(c_ptr), value :: client
      type(c_ptr), value :: handle
      integer(c_int32_t), intent(out) :: out_value
      integer(c_int), value :: timeout_ms
    end function

    ! wait_for_int64
    integer(c_int) function radex_client_wait_for_int64(client, handle, out_value, timeout_ms) &
        bind(C, name="radex_client_wait_for_int64")
      use iso_c_binding
      type(c_ptr), value :: client
      type(c_ptr), value :: handle
      integer(c_int64_t), intent(out) :: out_value
      integer(c_int), value :: timeout_ms
    end function

    ! wait_for_float32
    integer(c_int) function radex_client_wait_for_float32(client, handle, out_value, timeout_ms) &
        bind(C, name="radex_client_wait_for_float32")
      use iso_c_binding
      type(c_ptr), value :: client
      type(c_ptr), value :: handle
      real(c_float), intent(out) :: out_value
      integer(c_int), value :: timeout_ms
    end function

    ! wait_for_float64
    integer(c_int) function radex_client_wait_for_float64(client, handle, out_value, timeout_ms) &
        bind(C, name="radex_client_wait_for_float64")
      use iso_c_binding
      type(c_ptr), value :: client
      type(c_ptr), value :: handle
      real(c_double), intent(out) :: out_value
      integer(c_int), value :: timeout_ms
    end function

    ! wait_for_tensor_int32
    integer(c_int) function radex_client_wait_for_tensor_int32(client, handle, &
        out_data, max_elements, out_rank, out_dims, max_dims, timeout_ms) &
        bind(C, name="radex_client_wait_for_tensor_int32")
      use iso_c_binding
      type(c_ptr), value :: client
      type(c_ptr), value :: handle
      integer(c_int32_t), intent(out) :: out_data(*)
      integer(c_int), value :: max_elements
      integer(c_int), intent(out) :: out_rank
      integer(c_int), intent(out) :: out_dims(*)
      integer(c_int), value :: max_dims
      integer(c_int), value :: timeout_ms
    end function

    ! wait_for_tensor_int64
    integer(c_int) function radex_client_wait_for_tensor_int64(client, handle, &
        out_data, max_elements, out_rank, out_dims, max_dims, timeout_ms) &
        bind(C, name="radex_client_wait_for_tensor_int64")
      use iso_c_binding
      type(c_ptr), value :: client
      type(c_ptr), value :: handle
      integer(c_int64_t), intent(out) :: out_data(*)
      integer(c_int), value :: max_elements
      integer(c_int), intent(out) :: out_rank
      integer(c_int), intent(out) :: out_dims(*)
      integer(c_int), value :: max_dims
      integer(c_int), value :: timeout_ms
    end function

    ! wait_for_tensor_float32
    integer(c_int) function radex_client_wait_for_tensor_float32(client, handle, &
        out_data, max_elements, out_rank, out_dims, max_dims, timeout_ms) &
        bind(C, name="radex_client_wait_for_tensor_float32")
      use iso_c_binding
      type(c_ptr), value :: client
      type(c_ptr), value :: handle
      real(c_float), intent(out) :: out_data(*)
      integer(c_int), value :: max_elements
      integer(c_int), intent(out) :: out_rank
      integer(c_int), intent(out) :: out_dims(*)
      integer(c_int), value :: max_dims
      integer(c_int), value :: timeout_ms
    end function

    ! wait_for_tensor_float64
    integer(c_int) function radex_client_wait_for_tensor_float64(client, handle, &
        out_data, max_elements, out_rank, out_dims, max_dims, timeout_ms) &
        bind(C, name="radex_client_wait_for_tensor_float64")
      use iso_c_binding
      type(c_ptr), value :: client
      type(c_ptr), value :: handle
      real(c_double), intent(out) :: out_data(*)
      integer(c_int), value :: max_elements
      integer(c_int), intent(out) :: out_rank
      integer(c_int), intent(out) :: out_dims(*)
      integer(c_int), value :: max_dims
      integer(c_int), value :: timeout_ms
    end function

  end interface

  ! =========================================================================
  ! Convenience Wrappers (hide string length parameters)
  ! =========================================================================

contains

  subroutine client_put_int32(client, key, value, stat)
    !! Fortran-friendly wrapper to put int32 scalar
    type(c_ptr), intent(in) :: client
    character(len=*), intent(in) :: key
    integer(c_int32_t), intent(in) :: value
    integer, intent(out), optional :: stat
    integer(c_int) :: ierr
    type(c_ptr) :: handle

    handle = radex_outgoing_handle_create(trim(key)//c_null_char)
    if (.not. c_associated(handle)) then
      if (present(stat)) stat = RADEX_ERR_UNKNOWN
      return
    end if
    ierr = radex_client_put_int32(client, handle, value)
    call radex_outgoing_handle_destroy(handle)
    if (present(stat)) stat = ierr
  end subroutine client_put_int32

  subroutine client_get_int32(client, key, value, stat)
    !! Fortran-friendly wrapper to get int32 scalar
    type(c_ptr), intent(in) :: client
    character(len=*), intent(in) :: key
    integer(c_int32_t), intent(out) :: value
    integer, intent(out), optional :: stat
    integer(c_int) :: ierr
    type(c_ptr) :: handle

    handle = radex_incoming_handle_create(trim(key)//c_null_char)
    if (.not. c_associated(handle)) then
      if (present(stat)) stat = RADEX_ERR_UNKNOWN
      return
    end if
    ierr = radex_client_get_int32(client, handle, value)
    call radex_incoming_handle_destroy(handle)
    if (present(stat)) stat = ierr
  end subroutine client_get_int32

  subroutine client_put_int64(client, key, value, stat)
    !! Fortran-friendly wrapper to put int64 scalar
    type(c_ptr), intent(in) :: client
    character(len=*), intent(in) :: key
    integer(c_int64_t), intent(in) :: value
    integer, intent(out), optional :: stat
    integer(c_int) :: ierr
    type(c_ptr) :: handle

    handle = radex_outgoing_handle_create(trim(key)//c_null_char)
    if (.not. c_associated(handle)) then
      if (present(stat)) stat = RADEX_ERR_UNKNOWN
      return
    end if
    ierr = radex_client_put_int64(client, handle, value)
    call radex_outgoing_handle_destroy(handle)
    if (present(stat)) stat = ierr
  end subroutine client_put_int64

  subroutine client_get_int64(client, key, value, stat)
    !! Fortran-friendly wrapper to get int64 scalar
    type(c_ptr), intent(in) :: client
    character(len=*), intent(in) :: key
    integer(c_int64_t), intent(out) :: value
    integer, intent(out), optional :: stat
    integer(c_int) :: ierr
    type(c_ptr) :: handle

    handle = radex_incoming_handle_create(trim(key)//c_null_char)
    if (.not. c_associated(handle)) then
      if (present(stat)) stat = RADEX_ERR_UNKNOWN
      return
    end if
    ierr = radex_client_get_int64(client, handle, value)
    call radex_incoming_handle_destroy(handle)
    if (present(stat)) stat = ierr
  end subroutine client_get_int64

  subroutine client_put_float32(client, key, value, stat)
    !! Fortran-friendly wrapper to put float32 scalar
    type(c_ptr), intent(in) :: client
    character(len=*), intent(in) :: key
    real(c_float), intent(in) :: value
    integer, intent(out), optional :: stat
    integer(c_int) :: ierr
    type(c_ptr) :: handle

    handle = radex_outgoing_handle_create(trim(key)//c_null_char)
    if (.not. c_associated(handle)) then
      if (present(stat)) stat = RADEX_ERR_UNKNOWN
      return
    end if
    ierr = radex_client_put_float32(client, handle, value)
    call radex_outgoing_handle_destroy(handle)
    if (present(stat)) stat = ierr
  end subroutine client_put_float32

  subroutine client_get_float32(client, key, value, stat)
    !! Fortran-friendly wrapper to get float32 scalar
    type(c_ptr), intent(in) :: client
    character(len=*), intent(in) :: key
    real(c_float), intent(out) :: value
    integer, intent(out), optional :: stat
    integer(c_int) :: ierr
    type(c_ptr) :: handle

    handle = radex_incoming_handle_create(trim(key)//c_null_char)
    if (.not. c_associated(handle)) then
      if (present(stat)) stat = RADEX_ERR_UNKNOWN
      return
    end if
    ierr = radex_client_get_float32(client, handle, value)
    call radex_incoming_handle_destroy(handle)
    if (present(stat)) stat = ierr
  end subroutine client_get_float32

  subroutine client_put_float64(client, key, value, stat)
    !! Fortran-friendly wrapper to put float64 scalar
    type(c_ptr), intent(in) :: client
    character(len=*), intent(in) :: key
    real(c_double), intent(in) :: value
    integer, intent(out), optional :: stat
    integer(c_int) :: ierr
    type(c_ptr) :: handle

    handle = radex_outgoing_handle_create(trim(key)//c_null_char)
    if (.not. c_associated(handle)) then
      if (present(stat)) stat = RADEX_ERR_UNKNOWN
      return
    end if
    ierr = radex_client_put_float64(client, handle, value)
    call radex_outgoing_handle_destroy(handle)
    if (present(stat)) stat = ierr
  end subroutine client_put_float64

  subroutine client_get_float64(client, key, value, stat)
    !! Fortran-friendly wrapper to get float64 scalar
    type(c_ptr), intent(in) :: client
    character(len=*), intent(in) :: key
    real(c_double), intent(out) :: value
    integer, intent(out), optional :: stat
    integer(c_int) :: ierr
    type(c_ptr) :: handle

    handle = radex_incoming_handle_create(trim(key)//c_null_char)
    if (.not. c_associated(handle)) then
      if (present(stat)) stat = RADEX_ERR_UNKNOWN
      return
    end if
    ierr = radex_client_get_float64(client, handle, value)
    call radex_incoming_handle_destroy(handle)
    if (present(stat)) stat = ierr
  end subroutine client_get_float64

  subroutine client_contains(client, key, exists, stat)
    !! Fortran-friendly wrapper to check if key exists
    type(c_ptr), intent(in) :: client
    character(len=*), intent(in) :: key
    logical, intent(out) :: exists
    integer, intent(out), optional :: stat
    integer(c_int) :: ierr
    type(c_ptr) :: handle

    handle = radex_incoming_handle_create(trim(key)//c_null_char)
    if (.not. c_associated(handle)) then
      if (present(stat)) stat = RADEX_ERR_UNKNOWN
      exists = .false.
      return
    end if
    ierr = radex_client_contains(client, handle)
    call radex_incoming_handle_destroy(handle)
    exists = (ierr == 1)
    if (present(stat)) stat = ierr
  end subroutine client_contains

end module radex
