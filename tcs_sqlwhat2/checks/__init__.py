from tcs_sqlwhat2.checks.has_funcs import (
    has_no_error,
    has_result,
    has_nrows,
    has_ncols,
    has_equal_value,
)
from tcs_sqlwhat2.checks.check_funcs import (
    allow_error,
    check_column,
    check_row,
    check_all_columns,
    lowercase,
    check_result,
    check_query,
)

# functions from protowhat, exposed in sqlwhat
from protowhat.checks.check_funcs import (
    check_node,
    check_edge,
    has_code,
    has_equal_ast,
    has_parsed_ast,
)
from protowhat.checks.check_logic import fail, multi, check_not, check_or, check_correct
from protowhat.checks.check_simple import has_chosen, success_msg, allow_errors
from protowhat.utils import _debug
