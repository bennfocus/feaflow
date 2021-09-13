from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

from pydantic import constr

from feaflow.abstracts import (
    ComputeUnit,
    FeaflowConfig,
    FeaflowConfigurableComponent,
    FeaflowModel,
)
from feaflow.exceptions import EngineHandleError


class Engine(FeaflowConfigurableComponent, ABC):
    @abstractmethod
    def new_session(self):
        """ :rtype: `feaflow.engine.EngineSession` """
        raise NotImplementedError


class EngineRunContext(FeaflowModel, ABC):
    template_context: Dict[str, Any] = {}
    engine: Engine


class ComputeUnitHandler(ABC):
    @classmethod
    def can_handle(cls, unit: ComputeUnit) -> bool:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def handle(cls, context: EngineRunContext, unit: ComputeUnit):
        raise NotImplementedError


class EngineSession(ABC):
    _handlers: List[Type[ComputeUnitHandler]] = None

    @abstractmethod
    def run(self, job):
        """ :type job: `feaflow.job.Job` """
        raise NotImplementedError

    def get_handlers(self) -> Optional[List[Type[ComputeUnitHandler]]]:
        return self._handlers

    def set_handlers(self, handlers: List[Type[ComputeUnitHandler]]):
        self._handlers = handlers

    def handle(self, context: EngineRunContext, job):
        """
        :type context: `EngineRunContext`
        :type job: `feaflow.job.Job`
        """
        # Handle Sources, then Computes, then Sinks
        for source in job.sources:
            self._handle_one_unit(context, source)
        for compute in job.computes:
            self._handle_one_unit(context, compute)
        for sink in job.sinks:
            self._handle_one_unit(context, sink)

    def _handle_one_unit(self, context: EngineRunContext, unit: ComputeUnit):
        _handled = False

        try:
            for handler in self._handlers:
                if not _handled and handler.can_handle(unit):
                    handler.handle(context, unit)
                    _handled = True
        except Exception as ex:
            raise EngineHandleError(str(ex), context, type(unit).__name__)

        if not _handled:
            raise EngineHandleError(f"Not handler found", context, type(unit).__name__)

    @abstractmethod
    def __enter__(self):
        """ :rtype: `feaflow.engine.EngineSession` """
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError


class EngineConfig(FeaflowConfig, ABC):
    impl_cls: Type[Engine]
    name: constr(regex=r"^[^_][\w]+$", strip_whitespace=True, strict=True)
