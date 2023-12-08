import pytest

from fir.cmd.builder import Cmd, CmdArg, CmdBuilder


@pytest.fixture
def default_cmd():
    def fn(): pass
    return Cmd(
        "test_cmd",
        "test description",
        aliases=["test", "apple"],
        func=fn)


@pytest.fixture
def default_arg():
    return CmdArg(
        "test_arg",
        "test arg description",
        aliases=["test", "banana"],
        nargs="+")


def test_cmd_builder_register(default_cmd):
    builder = CmdBuilder()
    builder.register_command(default_cmd)

    assert len(builder.cmds.keys()) == 1
    assert builder.cmds["fn"] is not None
    assert builder.cmds.get("fn").name == default_cmd.name
    assert builder.cmds.get("fn").description == default_cmd.description
    assert builder.cmds.get("fn").aliases == default_cmd.aliases
    assert builder.cmds.get("fn").func == default_cmd.func

    def override_fn(): pass
    builder.register_command(default_cmd, func=override_fn)
    assert len(builder.cmds.keys()) == 2
    assert builder.cmds[override_fn.__name__] is not None
    assert builder.cmds[override_fn.__name__].func == override_fn


def test_cmd_builder_wrapper(default_cmd, default_arg):
    builder = CmdBuilder()
    builder.register_command(default_cmd) \
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
