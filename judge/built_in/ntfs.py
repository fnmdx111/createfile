# encoding: utf-8
rule1 = ['ntfs_mace_congruent()', '新建（下载）', False]

rule2 = ['ctg_eq(C) & ctg_eq(M)'
      ' & (_.SI_E > max_(SI_A, FN_E, FN_A))',
         '重命名（卷内移动）',
         False]

rule3 = ['attr_eq(FN)'
      ' & approx_eq(FN_C, SI_E, SI_A)'
      ' & (min_(SI_E, SI_A, FN_ALL) > max_(SI_C, SI_M))',
         '跨卷移动',
         False]

rule4 = ['attr_eq(FN)'
      ' & approx_eq(FN_C, SI_C, SI_E, SI_A)'
      ' & (min_(SI_C, SI_E, SI_A, FN_ALL) > _.SI_M)',
         '复制（解压）',
         False]

rule5 = ['approx_eq(SI_M, SI_E)'
      ' & (min_(SI_M, SI_E) > max_(FN_ALL, SI_C, SI_A))',
         '编辑文件',
         False]

rule6 = ['(_.SI_E > _.SI_A)'
      ' & (min_(SI_E, SI_A) > max_(SI_C, FN_ALL))'
      ' & (_.SI_E != _.SI_M)'
      ' & (_.FN_M != _.SI_M)',
         '编辑文件 M被修改',
         True]

rule7 = ['(_.SI_E > max_(FN_ALL, SI_M))'
      ' & approx_eq(FN_ALL, SI_M)'
      ' & (min_(FN_ALL, SI_M) > _.SI_C)',
         '重命名文件 C往前改',
         True]

rule8 = ['(_.SI_E > max_(SI_A, FN_ALL))'
      ' & approx_eq(SI_A, FN_ALL)'
      ' & (min_(SI_A, FN_ALL) > _.SI_M)'
      ' & (_.SI_C != _.SI_E)'
      ' & (_.SI_C != _.FN_C)',
         '复制文件 C被修改',
         True]

rule9 = ['(_.SI_E > max_(SI_C, FN_ALL))'
      ' & approx_eq(SI_C, FN_ALL)'
      ' & (min_(SI_C, FN_ALL) > _.SI_M)'
      ' & (_.SI_A != _.SI_E)'
      ' & (_.SI_A != _.FN_A)',
          '复制文件 A被修改',
          True]

rule10 = ['(_.SI_M != _.SI_E)'
       ' & (min_(SI_M, SI_E) > max_(SI_C, SI_A, FN_ALL))'
       ' & approx_eq(SI_C, SI_A, FN_ALL)',
          '复制文件 M往后改',
          True]

rules = [rule1, rule2, rule3,rule4, rule5, rule6, rule7, rule8, rule9, rule10]
