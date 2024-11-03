import React from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  ScheduleConfig as ScheduleConfigType,
  ScheduleType,
} from "@/types/workflow.types";

interface ScheduleConfigProps {
  config?: ScheduleConfigType;
  onChange: (config: ScheduleConfigType) => void;
}

const defaultIntervalConfig = {
  value: 5,
  unit: "minutes" as const,
};

const defaultSpecificTimeConfig = {
  time: "09:00",
  timezone: "UTC",
  days: ["monday"] as Array<
    | "monday"
    | "tuesday"
    | "wednesday"
    | "thursday"
    | "friday"
    | "saturday"
    | "sunday"
  >,
};

const defaultConfig: ScheduleConfigType = {
  scheduleType: "interval",
  timezone: "UTC",
  interval: defaultIntervalConfig,
  specificTime: defaultSpecificTimeConfig,
};

type DayOfWeek =
  | "monday"
  | "tuesday"
  | "wednesday"
  | "thursday"
  | "friday"
  | "saturday"
  | "sunday";
const days: Array<DayOfWeek> = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
];

export const ScheduleConfig: React.FC<ScheduleConfigProps> = ({
  config = defaultConfig,
  onChange,
}) => {
  const handleScheduleTypeChange = (value: ScheduleType) => {
    onChange({
      ...defaultConfig,
      scheduleType: value,
    });
  };

  return (
    <div className="space-y-4">
      <div>
        <Label>Schedule Type</Label>
        <Select
          value={config.scheduleType}
          onValueChange={handleScheduleTypeChange}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="cron">Cron Expression</SelectItem>
            <SelectItem value="interval">Interval</SelectItem>
            <SelectItem value="specific-time">Specific Time</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {config.scheduleType === "cron" && (
        <div>
          <Label>Cron Expression</Label>
          <Input
            placeholder="*/5 * * * *"
            value={config.cronExpression ?? ""}
            onChange={(e) =>
              onChange({ ...config, cronExpression: e.target.value })
            }
          />
        </div>
      )}

      {config.scheduleType === "interval" && (
        <div className="space-y-2">
          <div>
            <Label>Interval Value</Label>
            <Input
              type="number"
              min={1}
              value={config.interval?.value ?? defaultIntervalConfig.value}
              onChange={(e) =>
                onChange({
                  ...config,
                  interval: {
                    value:
                      parseInt(e.target.value) || defaultIntervalConfig.value,
                    unit: config.interval?.unit ?? defaultIntervalConfig.unit,
                  },
                })
              }
            />
          </div>
          <div>
            <Label>Interval Unit</Label>
            <Select
              value={config.interval?.unit ?? defaultIntervalConfig.unit}
              onValueChange={(value: "minutes" | "hours" | "days") =>
                onChange({
                  ...config,
                  interval: {
                    value:
                      config.interval?.value ?? defaultIntervalConfig.value,
                    unit: value,
                  },
                })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="minutes">Minutes</SelectItem>
                <SelectItem value="hours">Hours</SelectItem>
                <SelectItem value="days">Days</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      )}

      {config.scheduleType === "specific-time" && (
        <div className="space-y-2">
          <div>
            <Label>Time</Label>
            <Input
              type="time"
              value={
                config.specificTime?.time ?? defaultSpecificTimeConfig.time
              }
              onChange={(e) =>
                onChange({
                  ...config,
                  specificTime: {
                    time: e.target.value,
                    timezone:
                      config.specificTime?.timezone ??
                      defaultSpecificTimeConfig.timezone,
                    days: config.specificTime?.days ?? [
                      ...defaultSpecificTimeConfig.days,
                    ],
                  },
                })
              }
            />
          </div>
          <div>
            <Label>Days</Label>
            <div className="grid grid-cols-2 gap-2">
              {days.map((day) => (
                <div key={day} className="flex items-center space-x-2">
                  <Checkbox
                    id={`day-${day}`}
                    checked={config.specificTime?.days.includes(day) ?? false}
                    onCheckedChange={(checked) => {
                      const currentDays = [
                        ...(config.specificTime?.days ??
                          defaultSpecificTimeConfig.days),
                      ];
                      const newDays = checked
                        ? [...currentDays, day]
                        : currentDays.filter((d) => d !== day);
                      onChange({
                        ...config,
                        specificTime: {
                          time:
                            config.specificTime?.time ??
                            defaultSpecificTimeConfig.time,
                          timezone:
                            config.specificTime?.timezone ??
                            defaultSpecificTimeConfig.timezone,
                          days: newDays,
                        },
                      });
                    }}
                  />
                  <Label htmlFor={`day-${day}`}>
                    {day.charAt(0).toUpperCase() + day.slice(1)}
                  </Label>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div>
        <Label>Timezone</Label>
        <Input
          placeholder="UTC"
          value={config.timezone}
          onChange={(e) => onChange({ ...config, timezone: e.target.value })}
        />
      </div>
    </div>
  );
};
