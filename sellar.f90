! Copyright (c) 2019 Daniel de Vries
! This code is licensed under MIT license (see LICENSE for details)
module sellar
    use, intrinsic :: iso_c_binding, only: c_double
    implicit none
    private
        integer, parameter :: dp = kind(0.d0)
    public d1, d2
contains
    !> @brief calculate y1 = d1(z1, z2, x1, y2) = z1^2 + z2 + x1 - 0.2*y2
    !!
    !! This function defines the mathematical equation for the first discipline (D1) of the Sellar problem.
    !!
    !! @param[in]    z1, z2, x1, y2    doubles
    !! @return    the result of the equation as a double
    pure function d1(z1, z2, x1, y2) result(y1) bind(c, name='d1')
        real(c_double), intent(in) :: z1, z2, x1, y2
        real(c_double)             :: y1
        y1 = z1**2_dp + z2 + x1 - 0.2_dp*y2
    end function d1

    !> @brief calculate y2 = d2(z1, z2, y1) = sqrt(y1) + z1 + z2
    !!
    !! This function defines the mathematical equation for the second discipline (D2) of the Sellar problem.
    !!
    !! @param[in]    z1, z2, x1, y2    doubles
    !! @return    the result of the equation as a double
    pure function d2(z1, z2, y1) result(y2) bind(c, name='d2')
        real(c_double), intent(in) :: z1, z2, y1
        real(c_double)             :: y2
        y2 = y1**0.5_dp + z1 + z2
    end function d2
end module sellar