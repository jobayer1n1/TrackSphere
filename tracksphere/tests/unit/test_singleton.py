from app.infrastructure.config import ConfigurationManager


def test_configuration_manager_singleton():
    ConfigurationManager.reset_instance()
    config1 = ConfigurationManager()
    config2 = ConfigurationManager()

    assert config1 is config2
    assert config1.database_url == config2.database_url
    assert config1.environment == config2.environment
