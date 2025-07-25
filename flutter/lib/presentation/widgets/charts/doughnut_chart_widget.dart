import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../core/theme/app_colors.dart';
import '../../../data/models/chart_data.dart';

class DoughnutChartWidget extends StatefulWidget {
  final DoughnutChartData chartData;
  final double height;

  const DoughnutChartWidget({
    Key? key,
    required this.chartData,
    this.height = 300,
  }) : super(key: key);

  @override
  State<DoughnutChartWidget> createState() => _DoughnutChartWidgetState();
}

class _DoughnutChartWidgetState extends State<DoughnutChartWidget> {
  int touchedIndex = -1;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: widget.height,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Column(
        children: [
          // Chart Section
          Expanded(
            flex: 3,
            child: Center(
              child: AspectRatio(
                aspectRatio: 1.0,
                child: PieChart(
                  PieChartData(
                    pieTouchData: PieTouchData(
                      touchCallback: (FlTouchEvent event, pieTouchResponse) {
                        setState(() {
                          if (!event.isInterestedForInteractions ||
                              pieTouchResponse == null ||
                              pieTouchResponse.touchedSection == null) {
                            touchedIndex = -1;
                            return;
                          }
                          touchedIndex = pieTouchResponse.touchedSection!.touchedSectionIndex;
                        });
                      },
                    ),
                    borderData: FlBorderData(show: false),
                    sectionsSpace: 2,
                    centerSpaceRadius: 50,
                    sections: widget.chartData.segments.asMap().entries.map((entry) {
                      final index = entry.key;
                      final segment = entry.value;
                      final isTouched = index == touchedIndex;
                      final fontSize = isTouched ? 16.0 : 12.0;
                      final radius = isTouched ? 70.0 : 60.0;
                      
                      return PieChartSectionData(
                        color: Color(segment.color),
                        value: segment.value,
                        title: '${segment.value.toInt()}%',
                        radius: radius,
                        titleStyle: TextStyle(
                          fontSize: fontSize,
                          fontWeight: FontWeight.bold,
                          color: AppColors.textPrimary,
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ),
            ),
          ),
          // Legend Section
          Expanded(
            flex: 2,
            child: Padding(
              padding: const EdgeInsets.only(top: 16),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: widget.chartData.segments.asMap().entries.map((entry) {
                  final index = entry.key;
                  final segment = entry.value;
                  final isSelected = index == touchedIndex;
                  
                  return Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      children: [
                        Container(
                          width: 12,
                          height: 12,
                          decoration: BoxDecoration(
                            color: Color(segment.color),
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            segment.label,
                            style: TextStyle(
                              color: isSelected ? AppColors.textPrimary : AppColors.textSecondary,
                              fontSize: isSelected ? 14 : 13,
                              fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                            ),
                          ),
                        ),
                        Text(
                          '${segment.value.toInt()}%',
                          style: TextStyle(
                            color: isSelected ? Color(segment.color) : AppColors.textSecondary,
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
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