from dataclasses import dataclass
from typing import Callable, Any

@dataclass(frozen=True)
class ToolSpec:
    name: str
    handler: Callable[..., Any]
    requires_approval: bool = True

class ToolRegistry:
    def __init__(self): self._tools={}
    def register(self,name,handler,requires_approval=True):
        if not callable(handler): raise TypeError("Tool handler must be callable")
        self._tools[name]=ToolSpec(name,handler,requires_approval)
    def execute(self,name,args,authorized=False):
        if name not in self._tools: raise ValueError(f"Tool '{name}' is not registered")
        spec=self._tools[name]
        if spec.requires_approval and not authorized: raise PermissionError(f"Tool '{name}' requires explicit user approval")
        if not isinstance(args,dict): raise TypeError("Tool arguments must be an object")
        return spec.handler(**args)
    def describe(self): return {k:{"requires_approval":v.requires_approval} for k,v in self._tools.items()}

registry=ToolRegistry()
def execute_registered_tool(name,args,authorized=False): return registry.execute(name,args,authorized)
