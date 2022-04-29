from tcs_sqlwhat2.State import State
from protowhat.Test import TestFail
from protowhat.Reporter import Reporter

from tcs_sqlwhat2.checks.check_funcs import dbconn, runQuery
from tcs_sqlwhat2.sct_syntax import SCT_CTX


def test_exercise(
    sct,
    student_code,
    student_result,
    student_conn,
    solution_code,
    solution_result,
    solution_conn,
    pre_exercise_code,
    ex_type,
    error,
    force_diagnose=False,
    debug=False,  # currently unused
):
    """
    """

    state = State(
        student_code=student_code,
        solution_code=solution_code,
        pre_exercise_code=pre_exercise_code,
        student_conn=student_conn,
        solution_conn=solution_conn,
        student_result=student_result,
        solution_result=solution_result,
        reporter=Reporter(errors=error),
        force_diagnose=force_diagnose,
    )

    SCT_CTX["Ex"].root_state = state

    try:
        exec(sct, SCT_CTX)
    except TestFail as tf:
        return tf.payload

    return state.reporter.build_final_payload()


def setup_state(stu_conn, sol_conn, stu_code, sol_code, pre_code):
    with dbconn(sol_conn) as conn:
        sol_res = runQuery(conn, f'{pre_code}\n{sol_code}')

    with dbconn(stu_conn) as conn:
        stu_res = runQuery(conn,  f'{pre_code}\n{stu_code}')

    state = State(
        student_code=stu_code,
        solution_code=sol_code,
        pre_exercise_code=pre_code,
        student_conn=sol_conn,
        solution_conn=stu_conn,
        student_result=stu_res,
        solution_result=sol_res,
        reporter=Reporter()
    )
    return state