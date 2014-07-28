# encoding: utf-8

rule1 = ['ntfs_mace_congruent()', '新建，下载，解压', False]

rule2 = ['ctg_eq(C) & ctg_eq(M)'
      ' & approx_eq(SI_E, SI_A)'
      ' & (min_(SI_E, SI_A) > max_(FN_E, FN_A))',
         '重命名，卷内移动',
         False]

rule3 = ['attr_eq(FN)'
      ' & approx_eq(FN_C, SI_E, SI_A)'
      ' & (min_(SI_E, SI_A, FN_ALL) > max_(SI_C, SI_M))',
         '跨卷移动',
         False]

rule4 = ['attr_eq(FN)'
      ' & approx_eq(FN_C, SI_C, SI_E, SI_A)'
      ' & (min_(SI_C, SI_E, SI_A, FN_ALL) > _.SI_M)',
         '复制',
         False]

rule5 = ['approx_eq(SI_M, SI_E, SI_A)'
      ' & (min_(SI_M, SI_E, SI_A) > max_(FN_ALL, SI_C))',
         '编辑文件',
         False]

rule6 = ['approx_eq(SI_E, SI_A)'
      ' & (min_(SI_E, SI_A) > max_(SI_C, FN_ALL))'
      ' & (_.SI_E != _.SI_M)',
         '编辑文件的M被修改',
         True]

rule7 = ['(_.SI_E > max_(FN_ALL, SI_M))'
      ' & approx_eq(FN_ALL, SI_M)'
      ' & (min_(FN_ALL, SI_M) > _.SI_C)',
         '重命名文件的C往前改',
         True]

rule8 = ['(_.SI_E > max_(SI_A, FN_ALL))'
      ' & approx_eq(SI_A, FN_ALL)'
      ' & (min_(SI_A, FN_ALL) > _.SI_M)'
      ' & (_.SI_C != _.SI_E)',
         '复制的文件修改C',
         True]

rule9 = ['(_.SI_E > max_(SI_C, FN_ALL))'
      ' & approx_eq(SI_C, FN_ALL)'
      ' & (min_(SI_C, FN_ALL) > _.SI_M)'
      ' & (_.SI_A != _.SI_E)',
          '复制的文件修改A',
          True]

rule10 = ['(_.SI_M != _.SI_E)'
       ' & (min_(SI_M, SI_E) > max_(SI_C, SI_A, FN_ALL))'
       ' & approx_eq(SI_C, SI_A, FN_ALL)',
          '复制的文件M往后改',
          True]
