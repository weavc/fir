import pytest

from fir.cmd.builder import Cmd, CmdArg, CmdBuilder


default_name = "test_cmd"
default_description = "test description"
aliases = ["test", "apple"]

@pytest.fixture
def default_arg():
    return CmdArg(
        "test_arg",
        "test arg description",
        aliases=["test", "banana"],
        nargs="+")


def test_cmd_builder_register():
    def fn(): pass
    builder = CmdBuilder()
    builder.register(default_name, fn, description=default_description, aliases=aliases)

    assert len(builder.cmds.keys()) == 1
    assert builder.cmds["fn"] is not None
    assert builder.cmds.get("fn").name == default_name
    assert builder.cmds.get("fn").description == default_description
    assert builder.cmds.get("fn").aliases == aliases
    assert builder.cmds.get("fn").func == fn

    def override_fn(): pass
    builder.register(default_name, override_fn, description=default_description, aliases=aliases)
    assert len(builder.cmds.keys()) == 2
    assert builder.cmds[override_fn.__name__] is not None
    assert builder.cmds[override_fn.__name__].func == override_fn


def test_cmd_builder_wrapper(default_arg):
    def fn(): pass
    builder = CmdBuilder()
    builder.register(default_name, fn, description=default_description, aliases=aliases) \
        .with_optional(
            default_arg.with_overrides("opt1"),
            default_arg.with_overrides("opt2")) \
        .with_flag(default_arg.with_overrides(name="flag1")) \
        .with_positional(default_arg.with_overrides(name="arg1"))

    cmd = builder.cmds.get("fn")
    assert len(cmd.optionals) == 2
    assert len(cmd.flags) == 1
    assert len(cmd.args) == 1
    assert cmd.flags[0].name == "flag1"
    assert cmd.args[0].name == "arg1"
    for o in cmd.optionals:
        assert o.name.startswith("opt")
