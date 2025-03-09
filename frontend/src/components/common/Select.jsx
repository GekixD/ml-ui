import React from 'react';

export const Select = ({
    label,
    value,
    onChange,
    options,
    multiple
}) => {
    return (
        <div className="flex flex-col space-y-2">
            <label className="text-sm font-medium text-gray-700">{label}</label>
            <select
                value={value}
                onChange={(e) => {
                    if (multiple) {
                        const values = Array.from(e.target.selectedOptions).map(opt => opt.value);
                        onChange(values);
                    } else {
                        onChange(e.target.value);
                    }
                }}
                multiple={multiple}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
                {options.map((option) => (
                    <option key={option.value} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </select>
        </div>
    );
};