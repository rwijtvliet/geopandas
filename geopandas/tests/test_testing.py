import numpy as np

from shapely.geometry import Point, Polygon
from pandas import Series

from geopandas import GeoDataFrame, GeoSeries
from geopandas.array import from_shapely

from geopandas.testing import assert_geodataframe_equal, assert_geoseries_equal
import pytest

s1 = GeoSeries(
    [
        Polygon([(0, 0), (2, 0), (2, 2), (0, 2)]),
        Polygon([(2, 2), (4, 2), (4, 4), (2, 4)]),
    ]
)
s2 = GeoSeries(
    [
        Polygon([(0, 2), (0, 0), (2, 0), (2, 2)]),
        Polygon([(2, 2), (4, 2), (4, 4), (2, 4)]),
    ]
)


s3 = Series(
    [
        Polygon([(0, 2), (0, 0), (2, 0), (2, 2)]),
        Polygon([(2, 2), (4, 2), (4, 4), (2, 4)]),
    ]
)

a = from_shapely(
    [
        Polygon([(0, 2), (0, 0), (2, 0), (2, 2)]),
        Polygon([(2, 2), (4, 2), (4, 4), (2, 4)]),
    ]
)

s4 = Series(a)

df1 = GeoDataFrame({"col1": [1, 2], "geometry": s1})
df2 = GeoDataFrame({"col1": [1, 2], "geometry": s2})

s4 = s1.copy()
s4.crs = 4326
s5 = s2.copy()
s5.crs = 27700
df4 = GeoDataFrame(
    {"col1": [1, 2], "geometry": s1.copy(), "geom2": s4.copy(), "geom3": s5.copy()},
    crs=3857,
)
df5 = GeoDataFrame(
    {"col1": [1, 2], "geometry": s1.copy(), "geom3": s5.copy(), "geom2": s4.copy()},
    crs=3857,
)


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_geoseries():
    assert_geoseries_equal(s1, s2)
    assert_geoseries_equal(s1, s3, check_series_type=False, check_dtype=False)
    assert_geoseries_equal(s3, s2, check_series_type=False, check_dtype=False)
    assert_geoseries_equal(s1, s4, check_series_type=False)

    with pytest.raises(AssertionError):
        assert_geoseries_equal(s1, s2, check_less_precise=True)


def test_geodataframe():
    assert_geodataframe_equal(df1, df2)

    with pytest.raises(AssertionError):
        assert_geodataframe_equal(df1, df2, check_less_precise=True)

    with pytest.raises(AssertionError):
        assert_geodataframe_equal(df1, df2[["geometry", "col1"]])

    assert_geodataframe_equal(df1, df2[["geometry", "col1"]], check_like=True)

    df3 = df2.copy()
    df3.loc[0, "col1"] = 10
    with pytest.raises(AssertionError):
        assert_geodataframe_equal(df1, df3)

    assert_geodataframe_equal(df5, df4, check_like=True)
    df5.geom2.crs = 3857
    with pytest.raises(AssertionError):
        assert_geodataframe_equal(df5, df4, check_like=True)


def test_equal_nans():
    s = GeoSeries([Point(0, 0), np.nan])
    assert_geoseries_equal(s, s.copy())
    assert_geoseries_equal(s, s.copy(), check_less_precise=True)


def test_no_crs():
    df1 = GeoDataFrame({"col1": [1, 2], "geometry": s1}, crs=None)
    df2 = GeoDataFrame({"col1": [1, 2], "geometry": s1}, crs={})
    assert_geodataframe_equal(df1, df2)


def test_ignore_crs_mismatch():
    df1 = GeoDataFrame({"col1": [1, 2], "geometry": s1.copy()}, crs="EPSG:4326")
    df2 = GeoDataFrame({"col1": [1, 2], "geometry": s1}, crs="EPSG:31370")

    with pytest.raises(AssertionError):
        assert_geodataframe_equal(df1, df2)

    # assert that with `check_crs=False` the assert passes, and also does not
    # generate any warning from comparing both geometries with different crs
    with pytest.warns(None) as record:
        assert_geodataframe_equal(df1, df2, check_crs=False)

    assert len(record) == 0
