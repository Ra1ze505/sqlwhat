from protowhat.selectors import Selector, Dispatcher
from tcs_sqlwhat2.State import State, PARSER_MODULES
import importlib
from protowhat.Reporter import Reporter
from protowhat.Test import TestFail as TF
import pytest


@pytest.fixture
def ast():
    return importlib.import_module(PARSER_MODULES["postgresql"])


@pytest.fixture
def dispatcher():
    return Dispatcher.from_module(ast())


def test_selector_standalone():
    from ast import Expr, Num  # use python's builtin ast library

    Expr._priority = 0
    Num._priority = 1
    node = Expr(value=Num(n=1))
    sel = Selector(Num)
    sel.visit(node)
    assert isinstance(sel.out[0], Num)


def test_selector_on_self(ast):
    # Don't simplify terminals
    ast.Terminal.DEBUG = True
    terminal = ast.Terminal.from_text("test")
    sel = Selector(ast.Terminal)
    sel.visit(terminal)
    assert sel.out[0] == terminal


# tests using actual parsed ASTs ----------------------------------------------


def build_and_run(sql_expr, ast_class, ast_mod, priority=None):
    tree = ast_mod.parse(sql_expr)
    sel = Selector(ast_class, priority=priority)
    sel.visit(tree)
    return sel.out


def test_selector_on_script(ast):
    out = build_and_run("SELECT id FROM artists", ast.SelectStmt, ast)
    assert len(out) == 1
    assert type(out[0]) == ast.SelectStmt


def test_selector_default_priority(ast):
    out = build_and_run("SELECT id FROM artists", ast.Identifier, ast)
    assert len(out) == 0


def test_selector_set_high_priority(ast):
    out = build_and_run("SELECT id FROM artists", ast.Identifier, ast, priority=999)
    assert len(out) == 2
    assert all(type(v) == ast.Identifier for v in out)


def test_selector_set_low_priority(ast):
    out = build_and_run("SELECT id FROM artists", ast.Identifier, ast, priority=0)
    assert len(out) == 0


def test_selector_omits_subquery(ast):
    out = build_and_run(
        "SELECT a FROM x WHERE a = (SELECT b FROM y)", ast.SelectStmt, ast
    )
    assert len(out) == 1
    assert all(type(v) == ast.SelectStmt for v in out)
    assert out[0].target_list[0].fields == ["a"]


def test_selector_includes_subquery(ast):
    out = build_and_run(
        "SELECT a FROM x WHERE a = (SELECT b FROM y)", ast.SelectStmt, ast, priority=999
    )
    select1 = out[1]
    select2 = ast.parse(
        "SELECT b FROM y", start="subquery"
    )  # subquery is the parser rule for select statements
    assert repr(select1) == repr(select2)


def test_selector_head(ast):
    bin_expr = ast.parse("1 + 2 + 3", "expression")
    sel = Selector(ast.BinaryExpr)
    sel.visit(bin_expr)
    assert len(sel.out) == 1
    assert sel.out[0].right == "3"
    sel2 = Selector(ast.BinaryExpr)
    sel2.visit(sel.out[0], head=True)
    assert len(sel2.out) == 1
    assert sel2.out[0].left == "1"


def test_dispatch_select(dispatcher, ast):
    tree = ast.parse("SELECT id FROM artists")
    selected = dispatcher.find("SelectStmt", tree)[0]
    assert type(selected) == ast.SelectStmt


def test_selecting_base_nodes(ast):
    query = "SELECT a FROM b"
    antlr_tree = ast.parse_ast(ast.grammar, query, start="sql_script")
    ast_tree = ast.process_tree(antlr_tree)

    base_selector = Selector(ast.AstNode, "Query_block", strict=False, priority=3)
    base_selector.visit(ast_tree)
    found = base_selector.out
    assert len(found) == 1
    assert isinstance(found[0], ast.AstNode)
    assert found[0].__class__.__name__ == "Query_block"

    base_dispatch = Dispatcher(ast.AstNode, ast_mod=ast)
    select_stmt = base_dispatch.find("Query_block", ast_tree, priority=3)[0]
    assert select_stmt == found[0]
