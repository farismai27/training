import pytest
import numpy as np
from demo import sample_token


def test_sample_token_deterministic():
    """Test that temperature=0.0 always returns the highest probability token."""
    tokens = ["about", "would", "of", "we", "so"]
    probs = [0.6, 0.2, 0.1, 0.05, 0.05]
    
    for _ in range(10):
        result = sample_token(tokens, probs, temperature=0.0)
        assert result == "about", "Temperature 0 should always return highest probability token"


def test_sample_token_returns_valid_token():
    """Test that sampled token is always from the provided list."""
    tokens = ["about", "would", "of", "we", "so"]
    probs = [0.6, 0.2, 0.1, 0.05, 0.05]
    
    for temp in [0.0, 0.5, 1.0, 1.5]:
        result = sample_token(tokens, probs, temperature=temp)
        assert result in tokens, f"Result must be one of the input tokens"


def test_sample_token_single_token():
    """Test behavior with a single token."""
    tokens = ["only"]
    probs = [1.0]
    
    result = sample_token(tokens, probs, temperature=1.0)
    assert result == "only"


def test_sample_token_equal_probabilities():
    """Test with equal probabilities."""
    tokens = ["a", "b", "c"]
    probs = [0.33, 0.33, 0.34]
    
    result = sample_token(tokens, probs, temperature=1.0)
    assert result in tokens


def test_sample_token_temperature_affects_distribution():
    """Test that different temperatures produce different distributions."""
    tokens = ["rare", "common"]
    probs = [0.01, 0.99]
    
    # At temperature 0, should always get "common"
    results_low = [sample_token(tokens, probs, temperature=0.0) for _ in range(10)]
    assert all(r == "common" for r in results_low)
    
    # At high temperature, should occasionally get "rare" 
    # (though not guaranteed in small sample)
    results_high = [sample_token(tokens, probs, temperature=2.0) for _ in range(100)]
    assert "common" in results_high


def test_sample_token_very_low_temperature():
    """Test that very low temperature (near zero) behaves deterministically."""
    tokens = ["about", "would", "of"]
    probs = [0.6, 0.3, 0.1]
    
    result = sample_token(tokens, probs, temperature=1e-10)
    assert result == "about"


def test_sample_token_probabilities_sum():
    """Test that the function works even if probabilities don't sum to 1."""
    tokens = ["a", "b", "c"]
    probs = [2, 1, 1]  # Not normalized
    
    result = sample_token(tokens, probs, temperature=1.0)
    assert result in tokens
