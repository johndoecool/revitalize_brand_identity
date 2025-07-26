import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../core/theme/app_colors.dart';
import '../../../data/models/chart_data.dart' as chart_models;

class LineChartWidget extends StatefulWidget {
  final chart_models.LineChartData chartData;
  final double height;

  const LineChartWidget({
    Key? key,
    required this.chartData,
    this.height = 300,
  }) : super(key: key);

  @override
  State<LineChartWidget> createState() => _LineChartWidgetState();
}

class _LineChartWidgetState extends State<LineChartWidget> {
  int? touchedIndex;

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
                      height: 2,
                      decoration: BoxDecoration(
                        color: Color(series.color),
                        borderRadius: BorderRadius.circular(1),
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
            child: LineChart(
              LineChartData(
                minX: 0,
                maxX: (widget.chartData.xLabels.length - 1).toDouble(),
                minY: 0,
                maxY: 100,
                lineTouchData: LineTouchData(
                  enabled: true,
                  touchTooltipData: LineTouchTooltipData(
                    getTooltipItems: (List<LineBarSpot> touchedBarSpots) {
                      return touchedBarSpots.map((barSpot) {
                        final series = widget.chartData.series[barSpot.barIndex];
                        return LineTooltipItem(
                          '${series.brand}\n${barSpot.y.toInt()}%',
                          TextStyle(
                            color: Color(series.color),
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                          ),
                        );
                      }).toList();
                    },
                  ),
                  touchCallback: (FlTouchEvent event, LineTouchResponse? touchResponse) {
                    setState(() {
                      if (touchResponse == null || touchResponse.lineBarSpots == null) {
                        touchedIndex = null;
                      } else {
                        touchedIndex = touchResponse.lineBarSpots!.first.spotIndex;
                      }
                    });
                  },
                ),
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: true,
                  drawHorizontalLine: true,
                  verticalInterval: 1,
                  horizontalInterval: 20,
                  getDrawingVerticalLine: (value) {
                    return FlLine(
                      color: AppColors.glassBorder.withOpacity(0.2),
                      strokeWidth: 1,
                    );
                  },
                  getDrawingHorizontalLine: (value) {
                    return FlLine(
                      color: AppColors.glassBorder.withOpacity(0.2),
                      strokeWidth: 1,
                    );
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
                      reservedSize: 30,
                      interval: 1,
                      getTitlesWidget: (double value, TitleMeta meta) {
                        if (value.toInt() >= 0 && value.toInt() < widget.chartData.xLabels.length) {
                          return SideTitleWidget(
                            axisSide: meta.axisSide,
                            child: Text(
                              widget.chartData.xLabels[value.toInt()],
                              style: TextStyle(
                                color: AppColors.textSecondary,
                                fontSize: 10,
                              ),
                            ),
                          );
                        }
                        return const SideTitleWidget(
                          axisSide: AxisSide.bottom,
                          child: Text(''),
                        );
                      },
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
                lineBarsData: widget.chartData.series.map((series) {
                  return LineChartBarData(
                    spots: series.values.asMap().entries.map((entry) {
                      return FlSpot(entry.key.toDouble(), entry.value);
                    }).toList(),
                    color: Color(series.color),
                    barWidth: 2,
                    isStrokeCapRound: true,
                    dotData: FlDotData(
                      show: true,
                      getDotPainter: (spot, percent, barData, index) {
                        return FlDotCirclePainter(
                          radius: touchedIndex == index ? 5 : 3,
                          color: Color(series.color),
                          strokeWidth: touchedIndex == index ? 2 : 0,
                          strokeColor: AppColors.surfacePrimary,
                        );
                      },
                    ),
                    belowBarData: BarAreaData(
                      show: false,
                    ),
                  );
                }).toList(),
              ),
            ),
          ),
        ],
      ),
    );
  }
}