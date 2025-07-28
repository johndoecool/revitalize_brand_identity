class RadarChartData {
  final List<RadarDataPoint> dataPoints;
  final List<String> labels;

  RadarChartData({
    required this.dataPoints,
    required this.labels,
  });
}

class RadarDataPoint {
  final String brand;
  final List<double> values;
  final int color;

  RadarDataPoint({
    required this.brand,
    required this.values,
    required this.color,
  });
}

class DoughnutChartData {
  final List<DoughnutSegment> segments;

  DoughnutChartData({required this.segments});
}

class DoughnutSegment {
  final String label;
  final double value;
  final int color;

  DoughnutSegment({
    required this.label,
    required this.value,
    required this.color,
  });
}

class LineChartData {
  final List<LineDataSeries> series;
  final List<String> xLabels;

  LineChartData({
    required this.series,
    required this.xLabels,
  });
}

class LineDataSeries {
  final String brand;
  final List<double> values;
  final int color;

  LineDataSeries({
    required this.brand,
    required this.values,
    required this.color,
  });
}

class BarChartData {
  final List<BarDataSeries> series;
  final List<String> categories;

  BarChartData({
    required this.series,
    required this.categories,
  });
}

class BarDataSeries {
  final String brand;
  final List<double> values;
  final int color;

  BarDataSeries({
    required this.brand,
    required this.values,
    required this.color,
  });
}