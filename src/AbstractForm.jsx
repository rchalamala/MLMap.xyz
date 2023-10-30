import { useState, useEffect } from "react";

function AbstractForm({ abstractValue, onChange, onSubmit, onClose }) {
  const max_char_limit = 2500;
  const [charCount, setCharCount] = useState(abstractValue.length);
  const [inputValue, setInputValue] = useState(abstractValue);

  const handleInputChange = (event) => {
    const inputText = event.target.value;
    if (inputText.length <= max_char_limit) {
      setInputValue(inputText);
      onChange(event);
      setCharCount(inputText.length);
    }
  };

  const handleSubmit = () => {
    onChange(inputValue);
    abstractValue = inputValue;
    onSubmit();
  };

  useEffect(() => {
    setCharCount(inputValue.length);
  }, [inputValue]);

  return (
    <div className="fixed inset-0 z-999 flex items-center justify-center bg-black bg-opacity-75">
      <div className="form-container relative w-11/12 rounded-lg bg-white p-6 shadow-lg md:w-1/3">
        <button
          className="absolute right-2 top-2 text-gray-500"
          onClick={onClose}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
        <h2 className="mb-4 text-center text-2xl font-bold">
          Explore Your Abstract
        </h2>
        <textarea
          className="mb-4 h-32 w-full resize-none rounded-lg border border-gray-300 p-2"
          placeholder="Paste your research abstract here..."
          value={inputValue}
          onChange={handleInputChange}
          maxLength={max_char_limit}
        />
        <div className="text-right text-sm text-gray-500">
          {charCount}/{max_char_limit} characters
        </div>
        <button
          className="w-full rounded-lg bg-green-600 px-4 py-2 font-bold text-white"
          onClick={onSubmit}
        >
          Submit
        </button>
      </div>
    </div>
  );
}

export default AbstractForm;
