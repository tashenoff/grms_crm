'use client';
import React from 'react';
import LeadCard from './LeadCard';

const STATUSES = [
  { key: 'accepted', label: 'Принято', color: 'green' },
  { key: 'in_progress', label: 'В работе', color: 'blue', includeStatuses: ['in_progress', 'new'] },
  { key: 'delivery', label: 'Доставка', color: 'cyan' },
  { key: 'declined', label: 'Отклонено', color: 'red' },
];

export default function KanbanBoard({ leads, onSelect, onEdit, onDelete }) {
  // Функция для фильтрации заявок по статусу
  const filterLeadsByStatus = (statusKey) => {
    // Находим конфигурацию для текущей колонки
    const statusConfig = STATUSES.find(s => s.key === statusKey);

    // Если есть поле includeStatuses, используем его для фильтрации
    if (statusConfig?.includeStatuses) {
      return leads.filter(lead => statusConfig.includeStatuses.includes(lead.status));
    }
    // Иначе фильтруем строго по ключу статуса колонки
    return leads.filter(lead => lead.status === statusKey);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <div className="flex justify-between items-center border-b pb-4 mb-6">
        <h1 className="text-2xl font-bold text-blue-600">Доска заявок</h1>
        <div className="text-sm text-gray-500">
          {leads.length} заявок в системе
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {STATUSES.map(({ key, label, color }) => (
          <div key={key} className={`bg-${color}-50 rounded-lg p-4 border border-${color}-200 status-column`}>
            <div className={`text-lg font-semibold text-${color}-700 mb-2 flex justify-between items-center`}>
              <span>{label}</span>
              <span className="text-sm bg-white px-2 py-0.5 rounded-full">
                {filterLeadsByStatus(key).length}
              </span>
            </div>
            <div className="space-y-4">
              {filterLeadsByStatus(key).length === 0 ? (
                <div className="text-center py-8 text-gray-500">Нет заявок</div>
              ) : (
                filterLeadsByStatus(key).map(lead => (
                  <LeadCard 
                    key={lead.id} 
                    lead={lead} 
                    onSelect={onSelect}
                    onEdit={onEdit}
                    onDelete={onDelete}
                  />
                ))
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}