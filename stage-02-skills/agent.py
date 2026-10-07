"""LangChain agent của stage 02: read_file, write_file + skill catalog trong system prompt."""

from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware, ToolCallLimitMiddleware
from langchain_openai import ChatOpenAI

import paths
from config import MODEL_CALL_LIMIT, TOOL_CALL_LIMIT, Settings
from observer import ObserverMiddleware
from prompts import build_system_prompt
from skill_catalog import Catalog, render_catalog, scan_skills
from tools import list_files, read_file, write_file
import langchain_openai.chat_models.base as _lc_base

# Patch for Google Gemini thought_signature compatibility with ChatOpenAI
_orig_create_chat_result = _lc_base.ChatOpenAI._create_chat_result
def _patched_create_chat_result(self, response, generation_info=None, **kwargs):
    chat_result = _orig_create_chat_result(self, response, generation_info, **kwargs)
    if hasattr(response, "choices") and response.choices:
        msg = response.choices[0].message
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for i, tc in enumerate(msg.tool_calls):
                extra = getattr(tc, "extra_content", None)
                if extra and i < len(chat_result.generations[0].message.tool_calls):
                    chat_result.generations[0].message.tool_calls[i]["extra_content"] = extra
    return chat_result
_lc_base.ChatOpenAI._create_chat_result = _patched_create_chat_result

_orig_lc_tool_call_to_openai = _lc_base._lc_tool_call_to_openai_tool_call
def _patched_lc_tool_call_to_openai(tool_call):
    d = _orig_lc_tool_call_to_openai(tool_call)
    if "extra_content" in tool_call:
        d["extra_content"] = tool_call["extra_content"]
    return d
_lc_base._lc_tool_call_to_openai_tool_call = _patched_lc_tool_call_to_openai

TOOLS = [read_file, write_file, list_files]



def build_model(settings: Settings) -> ChatOpenAI:
    kwargs = {"model": settings.model_name, "api_key": settings.api_key}
    if settings.base_url:
        kwargs["base_url"] = settings.base_url
    return ChatOpenAI(**kwargs)


def load_catalog() -> Catalog:
    return scan_skills(paths.WORKSPACE_DIR)


def system_prompt() -> str:
    return build_system_prompt(render_catalog(load_catalog()))


def capabilities() -> dict:
    catalog = load_catalog()
    return {"tools": [t.name for t in TOOLS], "skills": catalog.metadata(), "skill_diagnostics": catalog.diagnostics}


def build_agent(model):
    return create_agent(
        model=model,
        tools=TOOLS,
        system_prompt=system_prompt(),
        middleware=[
            ModelCallLimitMiddleware(run_limit=MODEL_CALL_LIMIT, exit_behavior="end"),
            ToolCallLimitMiddleware(run_limit=TOOL_CALL_LIMIT),
            ObserverMiddleware(),  # cuối danh sách = sát model/tool invocation nhất
        ],
    )
