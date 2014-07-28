# encoding: utf-8

_c_ = 'create'
_m_ = 'modify'
_a_ = 'access'
_e_ = 'mft'
_si_ = 'si'
_fn_ = 'fn'

C = _c_
M = _m_
A = _a_
E = _e_

SI = _si_
FN = _fn_

si_e = 'si_mft_time'
si_m = 'si_modify_time'
si_a = 'si_access_time'
si_c = 'si_create_time'
fn_e = 'fn_mft_time'
fn_m = 'fn_modify_time'
fn_a = 'fn_access_time'
fn_c = 'fn_create_time'

SI_E = si_e
SI_M = si_m
SI_A = si_a
SI_C = si_c
FN_E = fn_e
FN_M = fn_m
FN_A = fn_a
FN_C = fn_c

f_c = 'create_time'
f_a = 'access_date'
f_m = 'modify_time'

F_C = f_c
F_A = f_a
F_M = f_m

si_all = [si_a, si_c, si_e, si_m]
fn_all = [fn_a, fn_c, fn_e, fn_m]
f_all = [f_c, f_a, f_m]

SI_ALL = si_all
FN_ALL = fn_all
F_ALL = f_all

m_all = [fn_m, si_m]
a_all = [fn_a, si_a]
c_all = [fn_c, si_c]
e_all = [fn_e, si_e]

M_ALL = m_all
A_ALL = a_all
C_ALL = c_all
E_ALL = e_all
