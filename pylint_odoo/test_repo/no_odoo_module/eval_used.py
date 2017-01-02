# -*- coding: utf-8 -*-


def eval_from_param(param):
    """eval used from param"""
    param("c = 2")


def eval_from_other():
    """eval used from many ways"""
    my_dict = {
        'my_eval': eval,  # [eval-used]
    }
    my_list = [eval]  # [eval-used]

    my_var = eval  # [eval-used]
    # inferred case
    my_var('d = 3')  # [eval-used]
    eval_from_param(eval)  # [eval-used]
    return my_dict, my_list
