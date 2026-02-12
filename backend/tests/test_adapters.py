import pytest
from core.adapters.adapter_factory import AdapterFactory
from core.adapters.data_schemas import AdapterConfiguration


class TestAdapterFactory:

    def test_get_supported_frameworks(self):
        """Test framework list"""
        frameworks = AdapterFactory.get_supported_frameworks()
        assert "pit" in frameworks
        assert "stryker" in frameworks

    def test_adapter_configuration(self):
        """Test configuration serialization"""
        config = AdapterConfiguration(
            timeout_per_mutant_seconds=10.0,
            max_parallel_threads=8,
            verbose=True
        )

        # Convert to dict
        config_dict = config.to_dict()
        assert config_dict['timeout_per_mutant_seconds'] == 10.0

        # Reconstruct from dict
        config2 = AdapterConfiguration(**config_dict)
        assert config2.timeout_per_mutant_seconds == 10.0