# encoding: utf-8

DEF EOC_MAGIC = 0x0ffffff8
cdef inline int _is_eoc(unsigned int n):
    return n & EOC_MAGIC == EOC_MAGIC

cdef inline void operate(object c,
                         dict cluster_head,
                         dict obj,
                         object i)

cpdef find_cluster_lists(object self,
                         dict cluster_head,
                         dict obj,
                         Py_ssize_t number_of_fat_items)
