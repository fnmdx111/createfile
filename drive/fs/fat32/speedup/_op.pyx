# encoding: utf-8

cdef inline void operate(object c,
                         dict cluster_head,
                         dict obj,
                         object i):
    if c == 0:
        return

    cdef Py_ssize_t neg_one = -1

    head = cluster_head.pop(i, i)
    if head not in obj:
        obj[head] = [[head, head]]

    if _is_eoc(c):
        return
    else:
        cluster_list = obj[head]
        last_segment = cluster_list[neg_one]
        if last_segment[neg_one] + 1 == c:
            last_segment[neg_one] = c
        else:
            cluster_list.append([c, c])
    cluster_head[c] = head


cpdef find_cluster_lists(object self,
                         dict cluster_head,
                         dict obj,
                         Py_ssize_t number_of_fat_items):
    cdef Py_ssize_t i
    for i from 2 <= i < number_of_fat_items:
        operate(self._next_ul_int32(),
                cluster_head, obj,
                i)
