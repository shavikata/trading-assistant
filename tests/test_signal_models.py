from app.signals.signal_models import SignalCandidate


def test_signal_candidate_table_row_includes_score_and_reason() -> None:
    candidate = SignalCandidate(
        ticker="TEST",
        signal_date="2024-01-01",
        close_price=10.0,
        volume=1_000_000,
        avg_volume_20=800_000,
        volume_spike_ratio=1.25,
        atr_14=0.5,
        atr_14_prev=0.6,
        atr_compression_ratio=0.83,
        rsi_14=55.0,
        high_52w=12.0,
        distance_from_52w_high_pct=-16.67,
        entry_price=10.1,
        stop_loss=9.25,
        target_1=11.0,
        target_2=11.5,
        score=80,
        reason="volume spike 1.25x; RSI setup zone 55.0",
    )

    row = candidate.to_signal_table_row()

    assert row["score"] == 80
    assert row["reason"] == "volume spike 1.25x; RSI setup zone 55.0"