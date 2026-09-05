from __future__ import annotations

from desaparecidos.manifests import ManifestRow
from desaparecidos.search_video import (
    format_spanish_date,
    person_card_lines,
    search_video_timeline,
    video_canvas_size,
)


def test_full_hd_timeline_contains_complete_closing_sequence() -> None:
    timeline = search_video_timeline(60 * 24, 24)

    assert video_canvas_size(1920) == (1920, 1080)
    assert timeline.total == 60 * 24
    assert timeline.search == 40 * 24
    assert timeline.final_hold == 4 * 24
    assert timeline.final_fade_out == 24
    assert timeline.person_fade_in == 24
    assert timeline.person_hold == 3 * 24
    assert timeline.person_fade_out == 24
    assert timeline.title_fade_in == 24
    assert timeline.title_hold == 2 * 24
    assert timeline.title_fade_out == 24


def test_person_card_uses_spanish_labels_and_human_readable_dates() -> None:
    target = ManifestRow(
        kind="targets",
        line_number=2,
        values={
            "id": "persona",
            "name": "Nombre Apellido",
            "birth_date": "1953-07-25",
            "disappearance_date": "1976-07",
            "disappearance_place": "Montevideo",
        },
    )

    assert format_spanish_date("1953-07-25") == "25 de julio de 1953"
    assert person_card_lines(target) == [
        "Nombre Apellido",
        "Nacimiento · 25 de julio de 1953",
        "Desaparición · julio de 1976",
        "Lugar de desaparición · Montevideo",
    ]


def test_schedule_preserves_skips_contributions_and_all_closing_phases() -> None:
    from types import SimpleNamespace
    from desaparecidos.search_video import VideoSettings, video_schedule
    walk = SimpleNamespace(placed_after_frame=[1, 3], segment_frame_ids=['a', 'b', 'c', 'd'])
    timeline, holds = video_schedule(walk, 2, 4, VideoSettings(playback_mode='hold', contribution_seconds=3, scan_seconds=0.25))
    assert holds == [1, 12, 1, 12]
    assert timeline.search == sum(holds)
    assert timeline.total == sum(holds) + 20 * 4
    assert all(count > 0 for count in timeline.as_dict().values())


def test_shared_sequence_for_all_three_memorials_is_monochrome_and_causal(tmp_path) -> None:
    from types import SimpleNamespace
    import numpy as np
    from PIL import Image
    from desaparecidos.pipeline_core import AssemblyResult, TilePlacement
    from desaparecidos.search_video import VideoSettings, complete_search_video_frames, video_presentation_metadata
    target = ManifestRow(kind='targets', line_number=2, values={'id': 'person', 'name': 'Nombre Apellido'})
    patch = Image.new('RGB', (24, 24), (230, 20, 70))
    p = TilePlacement('found', 'found:0', patch, 0, 0, 0, 0)
    final = Image.new('RGB', (48, 64), 0)
    final.paste(patch)
    assembly = AssemblyResult(final, final, {'found': 1}, {'found:0': 1}, [p])
    walk = SimpleNamespace(result=assembly, placed_after_frame=[1], segment_frame_ids=['skip', 'found'])
    sources = [[{'id': 'skip', 'image': Image.new('RGB', (48, 64), 20)}, {'id': 'found', 'image': patch}]]
    seen = []
    def progress(walk, target, count):
        seen.append(count)
        return Image.new('RGB', (48, 64), 0)
    for artwork in ('seguimos-buscando', 'estan-en-todas-partes', 'todos-somos-familiares'):
        options = VideoSettings(contribution_seconds=2, scan_seconds=1)
        frames = list(complete_search_video_frames(sources, [target], [walk], [final], duration_seconds=1,
            fps=2, output_width=320, composition='split', render_progress=progress, settings=options, artwork=artwork))
        metadata = video_presentation_metadata(320, 1, 2, target_ids=['person'], settings=options, walks=[walk], artwork=artwork)
        assert len(frames) == metadata['actual_duration_seconds'] * 2
        assert metadata['closing_sequence'][-2:] == [artwork, 'https://desaparecidos.uy']
        assert seen[0] == 0 and frames[-1].getbbox() is None
        # Left search panel is visible while the right reconstruction is still empty.
        assert frames[0].crop((10, 25, 155, 170)).getbbox() is not None
        assert frames[0].crop((175, 25, 310, 170)).getbbox() is None
        for frame in frames:
            a = np.asarray(frame)
            assert frame.size == (320, 180)
            assert np.array_equal(a[:, :, 0], a[:, :, 1])
            assert np.array_equal(a[:, :, 1], a[:, :, 2])


def test_fragment_video_never_loads_unreviewed_people_context(tmp_path) -> None:
    from types import SimpleNamespace
    from PIL import Image, ImageDraw
    from desaparecidos.images import source_region_from_row
    from desaparecidos.pipeline_core import AssemblyResult, TilePlacement
    from desaparecidos.search_video import fragment_video_frames, VideoSettings
    source = Image.new('RGB', (96, 96), 'white')
    ImageDraw.Draw(source).rectangle((24, 24, 47, 47), fill='black')
    path = tmp_path / 'source.png'
    source.save(path)
    row = ManifestRow(kind='people', line_number=2, values={'id':'source', 'local_path':str(path), 'review_status':'approved',
        'face_x':'24','face_y':'24','face_width':'24','face_height':'24'})
    target = ManifestRow(kind='targets', line_number=2, values={'id':'target'})
    face = source_region_from_row(source, row, 'people')
    placement = TilePlacement('source','p',face,0,0,0,0)
    assembly = AssemblyResult(face, face, {'source':1}, {'p':1}, [placement])
    settings = SimpleNamespace(**VideoSettings(show_match_marks=False).__dict__, fps=2, duration_seconds=1, output_width=320, seed=17)
    frames = list(fragment_video_frames(assembly,target,settings,'todos-somos-familiares',[row],tmp_path/'people.csv'))
    # The only reviewed region is black; the white surrounding photograph must never appear.
    assert frames[0].crop((10,25,155,170)).getbbox() is None


def test_continuous_walk_advances_during_transfer_and_lands_once() -> None:
    from types import SimpleNamespace
    import numpy as np
    from PIL import Image
    from desaparecidos.pipeline_core import AssemblyResult, TilePlacement
    from desaparecidos.search_video import VideoSettings, complete_search_video_frames, video_schedule, placement_timing
    target = ManifestRow(kind='targets', line_number=2, values={'id':'target'})
    patch = Image.new('RGB', (16, 16), 'white')
    p = TilePlacement('0', 'crop', patch, 16, 16, 0, 0, 16, 16)
    final = Image.new('RGB', (64, 64), 0)
    final.paste(patch, (16, 16))
    walk = SimpleNamespace(result=AssemblyResult(final, final, {'0':1}, {'crop':1}, [p]),
        placed_after_frame=[0], segment_frame_ids=[str(i) for i in range(6)])
    sources = [[{'id':str(i), 'image':Image.new('RGB',(64,64),(20+i*20,)*3)} for i in range(6)]]
    options = VideoSettings(scan_seconds=0.25, contribution_seconds=1, show_match_marks=False)
    timeline, holds = video_schedule(walk, 600*8, 8, options)
    assert holds == [2]*6  # A long requested duration must not stretch the walk.
    assert timeline.search == 12
    assert placement_timing(walk, holds, 8, options)[0]['land_frame'] == 8
    counts = []
    def progress(walk, target, count):
        counts.append(count)
        return Image.new('RGB', (64,64), 0)
    frames = list(complete_search_video_frames(sources,[target],[walk],[final],duration_seconds=600,
        fps=8,output_width=320,composition='split',render_progress=progress,settings=options))
    assert len(frames) == timeline.total
    assert frames[0].getpixel((140,140)) == (20,20,20)
    assert frames[2].getpixel((140,140)) == (40,40,40)
    # The crop moves across the gutter before it is part of the accumulated portrait.
    assert not np.array_equal(np.asarray(frames[2]),np.asarray(frames[3]))
    destination = (217,68)
    assert frames[0].getpixel(destination) == (0,0,0)
    assert frames[8].getpixel(destination) == (255,255,255)
    assert frames[11].getpixel(destination) == (255,255,255)
    assert set(counts) == {0}


def test_last_transfer_finishes_before_final_image_hold() -> None:
    from types import SimpleNamespace
    from desaparecidos.search_video import VideoSettings, video_schedule, placement_timing
    walk = SimpleNamespace(placed_after_frame=[2],segment_frame_ids=['a','b','c'])
    settings = VideoSettings()
    timeline, holds = video_schedule(walk, 1, 24, settings)
    event = placement_timing(walk, holds, 24, settings)[0]
    assert event['launch_frame'] == 8 and event['land_frame'] == 26
    assert timeline.search == 27


def test_catalogue_name_is_presented_given_names_first() -> None:
    target = ManifestRow(kind='targets', line_number=2,
        values={'id': 'person', 'name': 'Abeledo Sotuyo, Horacio Adolfo'})
    assert person_card_lines(target)[0] == 'Horacio Adolfo Abeledo Sotuyo'
    assert target.values['name'] == 'Abeledo Sotuyo, Horacio Adolfo'


def test_closing_fades_pass_through_black_and_finish_with_website() -> None:
    from types import SimpleNamespace
    from PIL import Image
    from desaparecidos.pipeline_core import AssemblyResult
    from desaparecidos.search_video import VideoSettings, complete_search_video_frames, video_schedule, _title_card
    final = Image.new('RGB', (64, 64), 'white')
    walk = SimpleNamespace(result=AssemblyResult(final, final, {}, {}, []),
        placed_after_frame=[], segment_frame_ids=['a'])
    target = ManifestRow(kind='targets', line_number=2, values={'id': 'person'})
    options = VideoSettings()
    timeline, _ = video_schedule(walk, 1, 4, options)
    frames = list(complete_search_video_frames([[{'id':'a', 'image':final}]], [target], [walk], [final],
        duration_seconds=1, fps=4, output_width=320, composition='split',
        render_progress=lambda *args: final, settings=options))
    phases = {}
    offset = 0
    for name, count in timeline.as_dict().items():
        phases[name] = frames[offset:offset + count]
        offset += count
    assert phases['search_fade_out'][-1].getbbox() is None
    assert phases['final_fade_in'][0].getbbox() is None
    assert phases['final_fade_in'][-1] == phases['final_hold'][0]
    assert phases['title_fade_out'][-1].getbbox() is None
    assert phases['website_fade_in'][0].getbbox() is None
    assert phases['website_hold'][0] == _title_card((320, 180), 'https://desaparecidos.uy')
    assert frames[-1].getbbox() is None
