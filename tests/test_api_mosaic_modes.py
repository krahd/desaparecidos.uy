from desaparecidos.api import create_app


def test_generate_request_exposes_mosaic_controls() -> None:
    schema = create_app().openapi()["components"]["schemas"]["GenerateRequest"]["properties"]
    assert schema["fragment_size"]["default"] == 36
    assert schema["reuse_limit"]["default"] == 1
    assert schema["composition_mode"]["default"] == "grid"
    assert schema["unique_tiles"]["default"] is True
    assert schema["matching_mode"]["default"] == "spatial"
