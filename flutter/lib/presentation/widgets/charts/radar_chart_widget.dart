import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../core/theme/app_colors.dart';
import '../../../data/models/chart_data.dart' as chart_models;

class RadarChartWidget extends StatelessWidget {
  final chart_models.RadarChartData chartData;
  final double height;

  const RadarChartWidget({
    Key? key,
    required this.chartData,
    this.height = 300,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height,
      padding: const EdgeInsets.all(16),
      child: RadarChart(
        RadarChartData(
          radarShape: RadarShape.polygon,
          tickCount: 5,
          ticksTextStyle: TextStyle(
            color: AppColors.textSecondary,
            fontSize: 10,
          ),
          radarBorderData: BorderSide(
            color: AppColors.glassBorder,
            width: 1,
          ),
          gridBorderData: BorderSide(
            color: AppColors.glassBorder.withOpacity(0.3),
            width: 1,
          ),
          tickBorderData: BorderSide(
            color: AppColors.glassBorder,
            width: 1,
          ),
          getTitle: (index, angle) {
            if (index < chartData.labels.length) {
              return RadarChartTitle(
                text: chartData.labels[index],
                angle: 0,
                positionPercentageOffset: 0.1,
              );
            }
            return const RadarChartTitle(text: '');
          },
          dataSets: chartData.dataPoints.map((dataPoint) {
            return RadarDataSet(
              fillColor: Color(dataPoint.color).withOpacity(0.1),
              borderColor: Color(dataPoint.color),
              borderWidth: 2,
              entryRadius: 3,
              dataEntries: dataPoint.values.asMap().entries.map((entry) {
                return RadarEntry(value: entry.value);
              }).toList(),
            );
          }).toList(),
          radarTouchData: RadarTouchData(
            enabled: true,
            touchCallback: (FlTouchEvent event, response) {
              // Handle touch events
            },
          ),
        ),
      ),
    );
  }
}