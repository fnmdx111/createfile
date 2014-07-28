# encoding: utf-8
"""
    drive.fs.fat32.speedup._op
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This is a cython module for speeding up the process of cluster list
    discovery.
"""
cdef inline void operate(object c,
                         dict cluster_head,
                         dict obj,
                         object i):
    """Operate with the integer just read.

    :param c: the integer just read.
    :param cluster_head: head cluster numbers of the cluster lists.
    :param obj: a dict storing the cluster lists found.
    :param i: the number of the integer just read.
    """

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
            if c in obj:
                cluster_list.extend(c)
            else:
                cluster_list.append([c, c])
    cluster_head[c] = head


cpdef find_cluster_lists(object self,
                         dict cluster_head,
                         dict obj,
                         Py_ssize_t number_of_fat_items):
    """Find the cluster lists.

    :param self: the partition object.
    :param cluster_head: head cluster numbers of the cluster lists.
    :param obj: a dict storing the cluster lists found.
    :param number_of_fat_items: the number of the integers in FAT.
    """

    cdef Py_ssize_t i
    for i from 2 <= i < number_of_fat_items:
        operate(self._next_ul_int32(),
                cluster_head, obj,
                i)
