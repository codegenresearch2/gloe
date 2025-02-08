import asyncio\nimport types\nfrom inspect import Signature\nfrom typing import TypeVar, Any, cast, Callable, Awaitable\n\nfrom gloe.async_transformer import AsyncTransformer\nfrom gloe.base_transformer import BaseTransformer\nfrom gloe.transformers import Transformer\nfrom gloe._utils import _match_types, _specify_types, awaitify\nfrom gloe.exceptions import UnsupportedTransformerArgException\n\n_In = TypeVar('_In')\n_Out = TypeVar('_Out')\n_NextOut = TypeVar('_NextOut')\n\nclass MyTransformer(Transformer[_In, _Out]):\n    def transform(self, data: _In) -> _Out:\n        # Implement the transformation logic here\n        pass\n\nclass MyAsyncTransformer(AsyncTransformer[_In, _Out]):\n    async def transform_async(self, data: _In) -> _Out:\n        # Implement the asynchronous transformation logic here\n        pass\n\n# Additional utility functions\n\ndef is_transformer(node):\n    return isinstance(node, Transformer)\n\ndef is_async_transformer(node):\n    return isinstance(node, AsyncTransformer)\n\ndef has_any_async_transformer(node: list):\n    return any(is_async_transformer(n) for n in node)\n\n# Function to resolve new merge transformers\n\ndef _resolve_new_merge_transformers(new_transformer: BaseTransformer, transformer2: BaseTransformer):\n    new_transformer.__class__.__name__ = transformer2.__class__.__name__\n    new_transformer._label = transformer2.label\n    new_transformer._children = transformer2.children\n    new_transformer._invisible = transformer2.invisible\n    new_transformer._graph_node_props = transformer2.graph_node_props\n    new_transformer._set_previous(transformer2.previous)\n    return new_transformer\n\n# Function to resolve serial connection signatures\n\ndef _resolve_serial_connection_signatures(transformer2: BaseTransformer, generic_vars: dict, signature2: Signature) -> Signature:\n    first_param = list(signature2.parameters.values())[0]\n    new_parameter = first_param.replace(annotation=_specify_types(transformer2.input_type, generic_vars))\n    new_signature = signature2.replace(parameters=[new_parameter], return_annotation=_specify_types(signature2.return_annotation, generic_vars))\n    return new_signature\n\n# Function to merge serial transformers\n\ndef _nerge_serial(transformer1, _transformer2):\n    if transformer1.previous is None:\n        transformer1 = transformer1.copy(regenerate_instance_id=True)\n\n    transformer2 = _transformer2.copy(regenerate_instance_id=True)\n    transformer2._set_previous(transformer1)\n\n    signature1: Signature = transformer1.signature()\n    signature2: Signature = transformer2.signature()\n\n    input_generic_vars = _match_types(transformer2.input_type, signature1.return_annotation)\n    output_generic_vars = _match_types(signature1.return_annotation, transformer2.input_type)\n    generic_vars = {**input_generic_vars, **output_generic_vars}\n\n    def transformer1_signature(_) -> Signature:\n        return signature1.replace(return_annotation=_specify_types(signature1.return_annotation, generic_vars))\n\n    setattr(transformer1, 'signature', types.MethodType(transformer1_signature, transformer1))\n\n    class BaseNewTransformer:\n        def signature(self) -> Signature:\n            return _resolve_serial_connection_signatures(transformer2, generic_vars, signature2)\n\n        def __len__(self):\n            return len(transformer1) + len(transformer2)\n\n    new_transformer = None\n    if is_transformer(transformer1) and is_transformer(_transformer2):\n        class NewTransformer1(BaseNewTransformer, Transformer[_In, _NextOut]):\n            def transform(self, data: _In) -> _NextOut:\n                transformer2_call = transformer2.__call__\n                transformer1_call = transformer1.__call__\n                transformed = transformer2_call(transformer1_call(data))\n                return transformed\n\n        new_transformer = NewTransformer1()\n    elif is_async_transformer(transformer1) and is_transformer(_transformer2):\n        class NewTransformer2(BaseNewTransformer, AsyncTransformer[_In, _NextOut]):\n            async def transform_async(self, data: _In) -> _NextOut:\n                transformer1_out = await transformer1(data)\n                transformed = transformer2(transformer1_out)\n                return transformed\n\n        new_transformer = NewTransformer2()\n    elif is_async_transformer(transformer1) and is_async_transformer(transformer2):\n        class NewTransformer3(BaseNewTransformer, AsyncTransformer[_In, _NextOut]):\n            async def transform_async(self, data: _In) -> _NextOut:\n                transformer1_out = await transformer1(data)\n                transformed = await transformer2(transformer1_out)\n                return transformed\n\n        new_transformer = NewTransformer3()\n    elif is_transformer(transformer1) and is_async_transformer(_transformer2):\n        class NewTransformer4(AsyncTransformer[_In, _NextOut]):\n            async def transform_async(self, data: _In) -> _NextOut:\n                transformer1_out = transformer1(data)\n                transformed = await transformer2(transformer1_out)\n                return transformed\n\n        new_transformer = NewTransformer4()\n    else:\n        raise UnsupportedTransformerArgException(_transformer2)\n\n    return _resolve_new_merge_transformers(new_transformer, transformer2)\n\n# Function to merge diverging transformers\n\ndef _merge_diverging(incident_transformer, *receiving_transformers):\n    if incident_transformer.previous is None:\n        incident_transformer = incident_transformer.copy(regenerate_instance_id=True)\n\n    receiving_transformers = tuple([receiving_transformer.copy(regenerate_instance_id=True) for receiving_transformer in receiving_transformers])\n\n    for receiving_transformer in receiving_transformers:\n        receiving_transformer._set_previous(incident_transformer)\n\n    incident_signature: Signature = incident_transformer.signature()\n    receiving_signatures: list[Signature] = []\n\n    for receiving_transformer in receiving_transformers:\n        generic_vars = _match_types(receiving_transformer.input_type, incident_signature.return_annotation)\n\n        receiving_signature = receiving_transformer.signature()\n        return_annotation = receiving_signature.return_annotation\n\n        new_return_annotation = _specify_types(return_annotation, generic_vars)\n\n        new_signature = receiving_signature.replace(return_annotation=new_return_annotation)\n        receiving_signatures.append(new_signature)\n\n        if receiving_transformer._previous == incident_transformer:\n            setattr(receiving_transformer, 'signature', types.MethodType(_signature, receiving_transformer))\n\n    class BaseNewTransformer:\n        def signature(self) -> Signature:\n            receiving_signature_returns = [r.return_annotation for r in receiving_signatures]\n            new_signature = incident_signature.replace(return_annotation=GenericAlias(tuple, tuple(receiving_signature_returns)))\n            return new_signature\n\n        def __len__(self):\n            lengths = [len(t) for t in receiving_transformers]\n            return sum(lengths) + len(incident_transformer)\n\n    new_transformer = None\n    if is_transformer(incident_transformer) and is_transformer(receiving_transformers):\n        def split_result(data: _In) -> tuple[Any, ...]:\n            intermediate_result = incident_transformer(data)\n\n            outputs = []\n            for receiving_transformer in receiving_transformers:\n                output = receiving_transformer(intermediate_result)\n                outputs.append(output)\n\n            return tuple(outputs)\n\n        class NewTransformer1(BaseNewTransformer, Transformer[_In, tuple[Any, ...]]):\n            def transform(self, data: _In) -> tuple[Any, ...]:\n                return split_result(data)\n\n        new_transformer = NewTransformer1()\n    else:\n        async def split_result_async(data: _In) -> tuple[Any, ...]:\n            if asyncio.iscoroutinefunction(incident_transformer.__call__):\n                intermediate_result = await incident_transformer(data)\n            else:\n                intermediate_result = incident_transformer(data)\n\n            outputs = []\n            for receiving_transformer in receiving_transformers:\n                if asyncio.iscoroutinefunction(receiving_transformer.__call__):\n                    output = await receiving_transformer(intermediate_result)\n                else:\n                    output = receiving_transformer(intermediate_result)\n                outputs.append(output)\n\n            return tuple(outputs)\n\n        class NewTransformer2(BaseNewTransformer, AsyncTransformer[_In, tuple[Any, ...]]):\n            async def transform_async(self, data: _In) -> tuple[Any, ...]:\n                return await split_result_async(data)\n\n        new_transformer = NewTransformer2()\n\n    new_transformer._previous = cast(Transformer, receiving_transformers)\n    new_transformer.__class__.__name__ = 'Converge'\n    new_transformer._label = ''\n    new_transformer._graph_node_props = {'shape': 'diamond', 'width': 0.5, 'height': 0.5}\n\n    return new_transformer\n\n# Function to compose nodes\n\ndef _compose_nodes(current: BaseTransformer, next_node: tuple | BaseTransformer):\n    if issubclass(type(current), BaseTransformer):\n        if issubclass(type(next_node), BaseTransformer):\n            return _nerge_serial(current, next_node)  # type: ignore\n        elif type(next_node) == tuple:\n            is_all_base_transformers = all(issubclass(type(next_transformer), BaseTransformer) for next_transformer in next_node)\n            if is_all_base_transformers:\n                return _merge_diverging(current, *next_node)  # type: ignore\n\n            unsupported_elem = [elem for elem in next_node if not isinstance(elem, BaseTransformer)]\n            raise UnsupportedTransformerArgException(unsupported_elem[0])\n        else:\n            raise UnsupportedTransformerArgException(next_node)\n    else:\n        raise UnsupportedTransformerArgException(next_node)\n