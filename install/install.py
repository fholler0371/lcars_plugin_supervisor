import tomllib
import pathlib
import sys
import asyncio
import os


async def install(parent_cfg: dict) -> dict:
    config_file = pathlib.Path('/'.join(__file__.split('/')[:-2])) / 'config/config.toml'
    cfg = {}
    out = {}
    for plugin in parent_cfg.get('plugins', []):
        if plugin.get('name') == 'supervisor':
            plugin_cfg = plugin
            break
    else:
        return out
    main = plugin_cfg.get('main', {})
    if not(folder := main.get('folder', False)):
        return out 
    folder = pathlib.Path(folder)
    if not folder.exists():
        p = await asyncio.subprocess.create_subprocess_shell(f'sudo mkdir -p {str(folder)}/.git', 
                                                                    stderr=asyncio.subprocess.PIPE, 
                                                                    stdout=asyncio.subprocess.PIPE)
        await p.wait()
        p = await asyncio.subprocess.create_subprocess_shell(f'sudo chown {os.getuid()}:{os.getgid()} -R {str(folder)}', 
                                                                    stderr=asyncio.subprocess.PIPE, 
                                                                    stdout=asyncio.subprocess.PIPE)
        await p.wait()
    if not(repo := main.get('remote', False)):
        return out
    base = folder
    folder = folder / '.git'
    repo_folder = repo.split('/')[-1].split('.')[0]
    if not ( folder / repo_folder).exists():
        p = await asyncio.subprocess.create_subprocess_shell(f'cd {str(folder)} ; git clone {repo}', 
                                                                    stderr=asyncio.subprocess.PIPE, 
                                                                    stdout=asyncio.subprocess.PIPE)
        await p.wait()
    cmd = f'{sys.executable} {(folder / repo_folder)}/install/install.py {base} {parent_cfg.get("setup", {}).get("lcars_base_folder")}'
    p = await asyncio.subprocess.create_subprocess_shell(cmd)
    await p.wait()
    return out

