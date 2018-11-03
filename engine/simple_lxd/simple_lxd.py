import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
import logging

logger = logging.getLogger(__name__)


class LXDError(Exception):
    pass


def launch(image, name, ephemeral=False, profile=None, config=None,
           instance_type=None):
    """Create and start containers from images.
    Syntax: lxc launch [<remote>:]<image> [<remote>:][<name>] [--ephemeral|-e]
        [--profile|-p <profile>...] [--config|-c <key=value>...]
        [--type|-t <instance type>]
    :param image:
    :param name:
    :param ephemeral:
    :param profile:
    :param config:
    :param instance_type:
    :return: str
    """
    logger.debug("Launching Linux container (image={:s}, name={:s}, ephemeral={:}, profile={:}, config={:}," \
                 " instance_type={:})...".format(image, name, ephemeral, profile, config, instance_type))

    command = ["lxc", "launch", image, name]
    if ephemeral:
        command.append("--ephemeral")
    if profile:
        command.append("--profile")
        command.append(profile)
    if config:
        command.append("--config")
        command.append(config)
    if instance_type:
        command.append("--type")
        command.append(instance_type)
    return _run(command)


def file_pull(container, source_path, target_path):
    """Pull files from containers.
    Syntax: lxc file pull [<remote>:]<container>/<path>
        [[<remote>:]<container>/<path>...] <target path>
    :return:
    """
    logger.debug("Pulling file {:s} from Linux container {:s} to {:s}...".format(source_path, container, target_path))

    command = ["lxc", "file", "pull"]
    from_path = os.path.join(container, source_path)
    command.append(container + from_path)
    command.append(target_path)
    return _run(command)


def file_push(container, source_path, target_path,
              uid=None, gid=None, mode=None):
    """Push files into containers.
    Syntax: lxc file push [--uid=UID] [--gid=GID] [--mode=MODE] <source path>
        [<source path>...] [<remote>:]<container>/<path>
    :return: str
    """
    logger.debug("Pushing file {:s} into Linux container {:s} in {:s} (uid={:}, gid={:}, mode={:})..."
                 .format(source_path, container, target_path, uid, gid, mode))

    # command = ["lxc", "file", "push", "--force-local", "--verbose"]
    command = ["lxc", "file", "push", "--debug", "--verbose"]

    if uid:
        command.append("--uid=")
        command.append(uid)
    if gid:
        command.append("--gid=")
        command.append(gid)
    if mode:
        command.append("--mode=")
        command.append(mode)
    command.append(source_path)
    command.append(container + target_path)

    return _run(command)


def stop(container):
    """Stop running containers.
    Syntax: lxc stop [<remote>:]<container> [[<remote>:]<container>...]
    :return: str
    """
    logger.debug("Stopping Linux container {:s}...".format(container))

    command = ["lxc", "stop"]
    if type(container) is str:
        command.append(container)
    elif type(container) is list:
        for c in container:
            command.append(c)
    return _run(command)


def delete(container):
    """Delete containers and snapshots.
    Syntax: lxc delete [<remote>:]<container>[/<snapshot>]
        [[<remote>:]<container>[/<snapshot>]...]
    :return: str
    """
    logger.debug("Deleting Linux container {:s}...".format(container))

    command = ["lxc", "delete"]
    if type(container) is str:
        command.append(container)
    elif type(container) is list:
        for c in container:
            command.append(c)
    return _run(command)


def execute(container, command_line, mode="non-interactive", env=None):
    """
    Execute commands in containers.
    Syntax: lxc exec [<remote>:]<container>
        [--mode=auto|interactive|non-interactive] [--env KEY=VALUE...]
        [--] <command line>
    :param container:
    :param command_line:
    :param mode:
    :param env:
    :return:
    """
    logger.debug("Executing command `{:}` in Linux container {:s} (mode={:}, env={:})..."
                 .format(command_line, container, mode, env))

    command = ["lxc", "exec", "--verbose", "--debug", container, "--mode={}".format(mode)]
    if env:
        command.append("--env")
        command.append(env)
    command.append("--")
    command.extend(command_line)
    return _run(command)


def profile_create(name, remote=None):
    """
    Create a new profile.
    Syntax: lxc profile create [<remote>:]<profile>
    :param remote:
    :param name:
    :return:
    """
    logger.debug("Creating Linux container profile {:} (remote={:})...".format(name))

    profile = "{}:{}".format(remote, name) if remote else name
    command = ["lxc", "profile", "create", profile]
    return _run(command)


def profile_copy(src_name, dst_name, src_remote=None, dst_remote=None):
    """
    Copy the profile.
    Syntax: lxc profile copy [<remote>:]<profile> [<remote>:]<profile>
    :param src_name:
    :param dst_name:
    :param src_remote:
    :param dst_remote:
    :return:
    """
    logger.debug("Copying Linux container profile {:s} to {:s} (src_remote={:}, dst_remote={:})..."
                 .format(src_name, dst_name, src_remote, dst_remote))

    src = "{}:{}".format(src_remote, src_name) if src_remote else src_name
    dst = "{}:{}".format(dst_remote, dst_name) if dst_remote else dst_name
    command = ["lxc", "profile", "copy", src, dst]
    return _run(command)


def profile_set(name, key, value, remote=None):
    """
    Set profile configuration.
    Syntax: lxc profile set [<remote>:]<profile> <key> <value>
    :param name:
    :param key:
    :param value:
    :param remote:
    :return:
    """
    logger.debug("Setting Linux container profile {:s} (key={:}, value={:}, remote={:})..."
                 .format(name, key, value, remote))

    profile = "{}:{}".format(remote, name) if remote else name
    command = ["lxc", "profile", "set", profile, key, value]
    return _run(command)


def profile_delete(name, remote=None):
    """
    Delete a profile.
    Syntax: lxc profile delete [<remote>:]<profile>
    :param name:
    :param remote:
    :return:
    """
    logger.debug("Deleting Linux container profile {:s} (remote={:})...".format(name, remote))

    profile = "{}:{}".format(remote, name) if remote else name
    command = ["lxc", "profile", "delete", profile]
    return _run(command)


def _run(command_args, timeout=60):
    logger.debug("Running command (timeout={:d}): {:s}".format(timeout, " ".join(command_args)))

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            process = Popen(command_args, stdout=PIPE, stderr=STDOUT, encoding="utf-8")
            process.wait(timeout)

            retval = process.poll()
            if retval != 0:
                logger.warning("Return value: {:}".format(retval))
        except subprocess.TimeoutExpired as e:
            logger.debug("Timeout expired on attempt {:d}. Retrying {:}".format(attempt+1, e))
            continue
        else:  # success
            retval = process.poll()
            stdout_str = process.stdout.read()

            if len(stdout_str.strip()) > 0:
                logger.debug("stdout+err:\n{:}".format(stdout_str.strip()))

            return process, retval, stdout_str
    else:  # all attempts failed.
        logger.debug("Max attempts ({:d}) tried.".format(max_attempts))


def _stdout_to_str(text_io_wrapper):
    line = text_io_wrapper.readline()
    total = ""
    while line:
        logger.debug(line)
        print(line, end="")
        line = text_io_wrapper.readline()
        total += line
    return total

