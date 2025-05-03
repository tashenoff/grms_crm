'use client';
import React from 'react';

/**
 * Универсальный компонент модального окна
 * @param {Object} props - Свойства компонента
 * @param {boolean} props.isOpen - Флаг, указывающий, открыто ли модальное окно
 * @param {Function} props.onClose - Функция, вызываемая при закрытии модального окна
 * @param {string} props.title - Заголовок модального окна (опционально)
 * @param {React.ReactNode} props.children - Содержимое модального окна
 * @param {string} props.size - Размер модального окна: 'sm', 'md', 'lg', 'xl' (по умолчанию 'md')
 * @param {boolean} props.showCloseButton - Показывать ли кнопку закрытия (по умолчанию true)
 * @param {boolean} props.showFooter - Показывать ли футер с кнопкой закрытия (по умолчанию false)
 * @returns {React.ReactElement}
 */
export default function Modal({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  size = 'md', 
  showCloseButton = true,
  showFooter = false
}) {
  if (!isOpen) return null;

  // Определение классов размера
  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  };

  // Обработчик клика по фону (закрытие модального окна)
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4"
      onClick={handleBackdropClick}
    >
      <div 
        className={`bg-white rounded-lg shadow-xl w-full ${sizeClasses[size]} relative overflow-hidden`}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Заголовок модального окна */}
        {title && (
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800">{title}</h2>
          </div>
        )}

        {/* Кнопка закрытия */}
        {showCloseButton && (
          <button 
            onClick={onClose}
            className="absolute top-3 right-3 text-gray-500 hover:text-gray-800 text-2xl font-bold"
            aria-label="Закрыть"
          >
            &times;
          </button>
        )}

        {/* Содержимое модального окна */}
        <div className="p-6">
          {children}
        </div>

        {/* Футер модального окна */}
        {showFooter && (
          <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end">
            <button 
              onClick={onClose} 
              className="px-4 py-2 bg-gray-300 text-gray-800 rounded hover:bg-gray-400 transition"
            >
              Закрыть
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
