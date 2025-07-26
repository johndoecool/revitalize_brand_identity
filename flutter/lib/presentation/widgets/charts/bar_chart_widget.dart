import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../core/theme/app_colors.dart';
import '../../../data/models/chart_data.dart' as chart_models;

class BarChartWidget extends StatefulWidget {
  final chart_models.BarChartData chartData;
  final double height;

  const BarChartWidget({
    Key? key,
    required this.chartData,
    this.height = 300,
  }) : super(key: key);

  @override
  State<BarChartWidget> createState() => _BarChartWidgetState();
}

class _BarChartWidgetState extends State<BarChartWidget> {
  int touchedGroupIndex = -1;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: widget.height,
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Legend
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: widget.chartData.series.map((series) {
              return Container(
                margin: const EdgeInsets.only(right: 16),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: Color(series.color),
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                    const SizedBox(width: 6),
                    Text(
                      series.brand,
                      style: TextStyle(
                        color: AppColors.textSecondary,
                        fontSize: 11,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 16),
          // Chart
          Expanded(
            child: BarChart(
              BarChartData(
                alignment: BarChartAlignment.spaceAround,
                maxY: 100,
                barTouchData: BarTouchData(
                  enabled: true,
                  touchTooltipData: BarTouchTooltipData(
                    getTooltipItem: (group, groupIndex, rod, rodIndex) {
                      final series = widget.chartData.series[rodIndex];
                      final category = widget.chartData.categories[groupIndex];
                      return BarTooltipItem(
                        '$category\n${series.brand}: ${rod.toY.toInt()}%',
                        TextStyle(
                          color: Color(series.color),
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                        ),
                      );
                    },
                  ),
                  touchCallback: (FlTouchEvent event, barTouchResponse) {
                    setState(() {
                      if (!event.isInterestedForInteractions ||
                          barTouchResponse == null ||
                          barTouchResponse.spot == null) {
                        touchedGroupIndex = -1;
                        return;
                      }
                      touchedGroupIndex = barTouchResponse.spot!.touchedBarGroupIndex;
                    });
                  },
                ),
                titlesData: FlTitlesData(
                  show: true,
                  rightTitles: const AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  topTitles: const AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      getTitlesWidget: (double value, TitleMeta meta) {
                        if (value.toInt() >= 0 && value.toInt() < widget.chartData.categories.length) {
                          return SideTitleWidget(
                            axisSide: meta.axisSide,
                            child: Padding(
                              padding: const EdgeInsets.only(top: 8.0),
                              child: Text(
                                widget.chartData.categories[value.toInt()],
                                style: TextStyle(
                                  color: AppColors.textSecondary,
                                  fontSize: 10,
                                  fontWeight: FontWeight.w500,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ),
                          );
                        }
                        return const SideTitleWidget(
                          axisSide: AxisSide.bottom,
                          child: Text(''),
                        );
                      },
                      reservedSize: 32,
                    ),
                  ),
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      interval: 20,
                      reservedSize: 40,
                      getTitlesWidget: (double value, TitleMeta meta) {
                        return SideTitleWidget(
                          axisSide: meta.axisSide,
                          child: Text(
                            '${value.toInt()}%',
                            style: TextStyle(
                              color: AppColors.textSecondary,
                              fontSize: 10,
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                ),
                borderData: FlBorderData(
                  show: true,
                  border: Border.all(
                    color: AppColors.glassBorder.withOpacity(0.3),
                    width: 1,
                  ),
                ),
                gridData: FlGridData(
                  show: true,
                  drawHorizontalLine: true,
                  drawVerticalLine: false,
                  horizontalInterval: 20,
                  getDrawingHorizontalLine: (value) {
                    return FlLine(
                      color: AppColors.glassBorder.withOpacity(0.2),
                      strokeWidth: 1,
                    );
                  },
                ),
                barGroups: _createBarGroups(),
              ),
            ),
          ),
        ],
      ),
    );
  }

  List<BarChartGroupData> _createBarGroups() {
    return widget.chartData.categories.asMap().entries.map((categoryEntry) {
      final categoryIndex = categoryEntry.key;
      final isTouched = categoryIndex == touchedGroupIndex;
      
      return BarChartGroupData(
        x: categoryIndex,
        barRods: widget.chartData.series.asMap().entries.map((seriesEntry) {
          final seriesIndex = seriesEntry.key;
          final series = seriesEntry.value;
          final value = series.values[categoryIndex];
          
          return BarChartRodData(
            toY: value,
            color: Color(series.color),
            width: isTouched ? 18 : 16,
            borderRadius: const BorderRadius.only(
              topLeft: Radius.circular(2),
              topRight: Radius.circular(2),
            ),
            backDrawRodData: BackgroundBarChartRodData(
              show: true,
              toY: 100,
              color: AppColors.glassBorder.withOpacity(0.1),
            ),
          );
        }).toList(),
        barsSpace: 4,
      );
    }).toList();
  }
}