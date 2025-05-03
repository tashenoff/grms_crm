'use client';
import React, { useState } from 'react';

const periods = [
  { value: 'all', label: 'Все время' },
  { value: 'today', label: 'Сегодня' },
  { value: 'week', label: 'Неделя' },
  { value: 'month', label: 'Месяц' },
  { value: 'custom', label: 'Указать даты' },
];

export default function StatsBlock({ stats, revenue, onPeriodChange, onCustomDateApply, onResetDB, period, customDates, setCustomDates }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <div className="flex justify-between items-center border-b pb-4 mb-6">
        <h1 className="text-2xl font-bold text-blue-600">Статистика заявок</h1>
        <div className="flex items-center space-x-2">
          <div className="flex items-center">
            <label htmlFor="period-select" className="mr-2 text-sm text-gray-600">Период:</label>
            <select id="period-select" className="border rounded px-2 py-1 text-sm" value={period} onChange={onPeriodChange}>
              {periods.map(p => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
            </select>
          </div>
          {period === 'custom' && (
            <div className="flex items-center space-x-2">
              <input type="date" value={customDates.start} onChange={e => setCustomDates(d => ({ ...d, start: e.target.value }))} className="border rounded px-2 py-1 text-sm" />
              <span className="text-gray-500">—</span>
              <input type="date" value={customDates.end} onChange={e => setCustomDates(d => ({ ...d, end: e.target.value }))} className="border rounded px-2 py-1 text-sm" />
              <button onClick={onCustomDateApply} className="bg-blue-500 hover:bg-blue-600 text-white text-xs px-3 py-1 rounded">Применить</button>
            </div>
          )}
          <button onClick={onResetDB} className="bg-red-500 hover:bg-red-600 text-white text-xs px-3 py-1 rounded">Сбросить базу</button>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-blue-50 rounded-lg p-4 text-center border border-blue-200">
          <div className="text-3xl font-bold text-blue-600">{stats.total}</div>
          <div className="text-sm text-gray-600">Всего заявок</div>
        </div>
        <div className="bg-green-50 rounded-lg p-4 text-center border border-green-200">
          <div className="text-3xl font-bold text-green-600">{stats.accepted}</div>
          <div className="text-sm text-gray-600">Принято</div>
        </div>
        <div className="bg-yellow-50 rounded-lg p-4 text-center border border-yellow-200">
          <div className="text-3xl font-bold text-yellow-600">{stats.in_progress}</div>
          <div className="text-sm text-gray-600">В работе</div>
        </div>
        <div className="bg-red-50 rounded-lg p-4 text-center border border-red-200">
          <div className="text-3xl font-bold text-red-600">{stats.declined}</div>
          <div className="text-sm text-gray-600">Отклонено</div>
        </div>
        <div className="bg-purple-50 rounded-lg p-4 text-center border border-purple-200">
          <div className="text-3xl font-bold text-purple-600">{stats.unique_clients || 0}</div>
          <div className="text-sm text-gray-600">Уникальных клиентов</div>
        </div>
      </div>
      <div className="bg-indigo-50 rounded-lg p-4 text-center border border-indigo-200 mt-6">
        <div className="text-lg font-medium text-indigo-700">Сумма принятых заявок</div>
        <div className="text-3xl font-bold text-indigo-900 mt-2">{revenue.toLocaleString('ru-RU', {minimumFractionDigits: 2, maximumFractionDigits: 2})} ₸</div>
      </div>
    </div>
  );
}
