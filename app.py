<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dynamic Data Analyzer</title>
    <!-- Load Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Load Papa Parse for CSV parsing -->
    <script src="https://unpkg.com/papaparse@5.4.1/papaparse.min.js"></script>
    <!-- Load Chart.js for visualization -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <!-- Load SheetJS for XLSX parsing -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <!-- Use Inter as the primary font -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap" rel="stylesheet">
    <style>
        /* Base styles using Inter for readability */
        body {
            font-family: 'Inter', sans-serif;
            transition: background-color 0.3s, color 0.3s;
        }
        /* Custom scrollbar for aesthetics */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
        .dark ::-webkit-scrollbar-thumb { background: #475569; }
        
        /* Transition for layout elements */
        .page-content { transition: opacity 0.3s ease-in-out; }

        /* Custom metric card style */
        .metric-card {
            background-color: var(--card-bg, #f8fafc);
            border: 1px solid var(--border-color, #e2e8f0);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.06);
            transition: all 0.3s;
        }
        .dark .metric-card {
            --card-bg: #1e293b;
            --border-color: #334155;
            box-shadow: none;
        }
    </style>
</head>
<body class="bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100" dir="ltr">
    <div id="app" class="flex h-screen overflow-hidden">

        <!-- Sidebar -->
        <div class="w-72 bg-white dark:bg-gray-800 shadow-xl p-6 flex flex-col flex-shrink-0 transition-colors duration-300 overflow-y-auto">
            <h1 class="text-3xl font-extrabold text-blue-600 dark:text-blue-400 mb-6" id="appTitle">Dynamic Analyzer</h1>
            
            <!-- Language Toggle Button -->
            <div class="mb-4 flex items-center justify-between">
                <span id="langToggleLabel" class="text-sm font-semibold text-gray-700 dark:text-gray-300">Change Language:</span>
                <button id="langToggle" class="p-2 text-sm font-bold rounded-xl bg-blue-500 text-white shadow-md hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 transition duration-150">
                    العربية
                </button>
            </div>

            <!-- Dark/Light Mode Button -->
            <div class="mb-6">
                <button id="themeToggle" class="w-full flex items-center justify-center p-3 rounded-xl font-bold transition duration-200 shadow-md
                    bg-gray-200 text-gray-800 hover:bg-gray-300
                    dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600">
                    <svg id="sunIcon" class="w-6 h-6 mr-2 hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
                    </svg>
                    <svg id="moonIcon" class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
                    </svg>
                    <span id="themeToggleText">Toggle Theme</span>
                </button>
            </div>
            
            <!-- Data Upload -->
            <h2 class="text-xl font-semibold mb-3 border-b pb-2 border-gray-200 dark:border-gray-700" id="dataSourceTitle">📥 Data Source</h2>
            
            <div class="space-y-4">
                <div id="dataStatus" class="p-3 rounded-xl text-sm border font-medium">
                    No data loaded yet. Please upload a file.
                </div>

                <!-- File Upload Input -->
                <div>
                    <label class="block text-sm font-medium" id="uploadLabel">Upload Data (CSV/XLSX)</label>
                    <input type="file" id="dataUpload" accept=".csv, .xlsx" class="w-full text-sm text-gray-900 dark:text-gray-200 mt-1
                        file:mr-4 file:py-2 file:px-4
                        file:rounded-full file:border-0
                        file:text-sm file:font-semibold
                        file:bg-blue-50 file:text-blue-700
                        hover:file:bg-blue-100 dark:file:bg-blue-800/50 dark:file:text-blue-300 dark:hover:file:bg-blue-800
                        cursor-pointer">
                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-1" id="uploadNote">Note: CSV is fully supported. XLSX uses mock data.</p>
                </div>

                <!-- Dynamic Value Column Selector (Multi-select) -->
                <div id="valueColContainer" class="hidden relative">
                    <label class="block text-sm font-medium mb-1" id="valueColLabel">Value Columns for KPIs</label>
                    <button id="kpiColSelectButton" type="button" class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 dark:text-gray-200 flex justify-between items-center text-left">
                        <span id="kpiColSelectButtonText" class="truncate">Select columns...</span>
                        <svg class="w-5 h-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 3a1 1 0 01.707.293l3 3a1 1 0 01-1.414 1.414L10 5.414 7.707 7.707a1 1 0 01-1.414-1.414l3-3A1 1 0 0110 3zm-3.707 9.293a1 1 0 011.414 0L10 14.586l2.293-2.293a1 1 0 011.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                    </button>
                    <!-- Popover for multi-select -->
                    <div id="kpiColumnPopover" class="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-60 overflow-y-auto hidden">
                        <!-- Checkboxes populated by JS -->
                    </div>
                </div>
            </div>
            
            <!-- Page Navigation -->
            <h2 class="text-xl font-semibold mt-8 mb-3 border-b pb-2 border-gray-200 dark:border-gray-700" id="selectPageTitle">Select Page</h2>
            <nav class="flex flex-col space-y-2" id="navContainer">
                <button data-page="dashboard" class="nav-button p-3 rounded-xl text-left font-medium bg-blue-500 text-white shadow-md hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 active">
                    <span class="mr-2">📊</span> <span data-text-key="navDashboard">Dashboard</span>
                </button>
                <button data-page="stats" class="nav-button p-3 rounded-xl text-left font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700">
                    <span class="mr-2">📈</span> <span data-text-key="navStats">Statistical Insights</span>
                </button>
                <button data-page="dataExplorer" class="nav-button p-3 rounded-xl text-left font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700">
                    <span class="mr-2">🗄️</span> <span data-text-key="navExplorer">Data Explorer</span>
                </button>
                <button data-page="forecasting" class="nav-button p-3 rounded-xl text-left font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700">
                    <span class="mr-2">🔮</span> <span data-text-key="navForecast">Forecasting</span>
                </button>
            </nav>
        </div>

        <!-- Main Content Area -->
        <main class="flex-grow p-8 overflow-y-auto">
            <div id="content" class="page-content">
                <!-- Content will be rendered here by JavaScript -->
            </div>
        </main>
    </div>

    <!-- Notification Bar (Hidden by default) -->
    <div id="notificationBar" class="fixed bottom-4 right-4 p-4 rounded-xl shadow-2xl z-50 transition-transform duration-500 transform translate-x-full hidden">
        <p id="notificationMessage" class="font-bold"></p>
    </div>

    <script>
        // --- GLOBAL STATE & MOCK DATA ---
        let appData = []; // Array of objects
        let appHeaders = []; // Array of string headers
        let currentLang = 'en';
        let myChart; // Chart.js instance
        let selectedKpiColumns = []; // Array of selected column names for KPIs
        let numericHeadersCache = []; // Cache for numeric headers

        // MOCK DATA 
        const MOCK_XLSX_DATA = [
            { "Quarter": 1, "Group": "Regina", "Item_Tax_Rate": 14, "Discounts": 0, "Value_After_Tax_Discount": 4479.93, "Value_After_Tax": 4479.93, "Value_Before_Tax_Discount": 3929.76 },
            { "Quarter": 1, "Group": "Regina", "Item_Tax_Rate": 14, "Discounts": 0, "Value_After_Tax_Discount": 5357.99, "Value_After_Tax": 5357.99, "Value_Before_Tax_Discount": 4699.99 },
            { "Quarter": 1, "Group": "Regina", "Item_Tax_Rate": 14, "Discounts": 0, "Value_After_Tax_Discount": 5075.83, "Value_After_Tax": 5075.83, "Value_Before_Tax_Discount": 4452.48 },
            { "Quarter": 1, "Group": "Regina", "Item_Tax_Rate": 14, "Discounts": 0, "Value_After_Tax_Discount": -28.00, "Value_After_Tax": -28.00, "Value_Before_Tax_Discount": -24.56 },
            { "Quarter": 1, "Group": "Regina", "Item_Tax_Rate": 14, "Discounts": 0, "Value_After_Tax_Discount": -210.00, "Value_After_Tax": -210.00, "Value_Before_Tax_Discount": -184.21 },
            { "Quarter": 1, "Group": "Regina", "Item_Tax_Rate": 14, "Discounts": 0, "Value_After_Tax_Discount": 238.00, "Value_After_Tax": 238.00, "Value_Before_Tax_Discount": 208.77 },
            { "Quarter": 2, "Group": "Regina", "Item_Tax_Rate": 14, "Discounts": 50, "Value_After_Tax_Discount": 1500.00, "Value_After_Tax": 1550.00, "Value_Before_Tax_Discount": 1315.79 },
            { "Quarter": 2, "Group": "Regina", "Item_Tax_Rate": 14, "Discounts": 0, "Value_After_Tax_Discount": 8200.00, "Value_After_Tax": 8200.00, "Value_Before_Tax_Discount": 7192.98 },
            { "Quarter": 2, "Group": "Regina", "Item_Tax_Rate": 14, "Discounts": 20, "Value_After_Tax_Discount": 410.00, "Value_After_Tax": 430.00, "Value_Before_Tax_Discount": 377.19 },
            { "Quarter": 2, "Group": "Regina", "Item_Tax_Rate": 14, "Discounts": 0, "Value_After_Tax_Discount": 12000.00, "Value_After_Tax": 12000.00, "Value_Before_Tax_Discount": 10526.32 },
            { "Quarter": 3, "Group": "Alpha", "Item_Tax_Rate": 10, "Discounts": 0, "Value_After_Tax_Discount": 900.00, "Value_After_Tax": 900.00, "Value_Before_Tax_Discount": 818.18 },
            { "Quarter": 3, "Group": "Alpha", "Item_Tax_Rate": 10, "Discounts": 10, "Value_After_Tax_Discount": 450.00, "Value_After_Tax": 460.00, "Value_Before_Tax_Discount": 409.09 },
            { "Quarter": 4, "Group": "Beta", "Item_Tax_Rate": 14, "Discounts": 0, "Value_After_Tax_Discount": 1200.00, "Value_After_Tax": 1200.00, "Value_Before_Tax_Discount": 1052.63 },
            { "Quarter": 4, "Group": "Beta", "Item_Tax_Rate": 14, "Discounts": 0, "Value_After_Tax_Discount": 1500.00, "Value_After_Tax": 1500.00, "Value_Before_Tax_Discount": 1315.79 },
            { "Quarter": 4, "Group": "Beta", "Item_Tax_Rate": 14, "Discounts": 0, "Value_After_Tax_Discount": 1600.00, "Value_After_Tax": 1600.00, "Value_Before_Tax_Discount": 1403.51 },
            { "Quarter": 1, "Group": "Charlie", "Item_Tax_Rate": 14, "Discounts": 0, "Value_After_Tax_Discount": 300.00, "Value_After_Tax": 300.00, "Value_Before_Tax_Discount": 263.16 },
        ];
        
        // --- TRANSLATIONS ---
        const translations = {
            en: {
                dir: 'ltr',
                pageTitle: 'Dynamic Analyzer', themeToggle: 'Toggle Theme', dataSource: '📥 Data Source',
                statusNoData: 'No data loaded yet. Please upload a file.',
                statusLoaded: (r, c) => `✅ Data Loaded! (${r} rows, ${c} columns)`,
                uploadLabel: 'Upload Data (CSV/XLSX)', uploadNote: 'Note: CSV is fully supported. XLSX uses mock data.',
                valueColLabel: 'Value Columns for KPIs', selectPage: 'Select Page',
                navDashboard: 'Dashboard', navStats: 'Statistical Insights', navExplorer: 'Data Explorer', navForecast: 'Forecasting',
                dashboardTitle: 'Dynamic Dashboard',
                kpiTotalOrders: 'Total Orders',
                kpiTotalCols: 'Total Columns',
                kpiTotal: (c) => `Total ${c}`, 
                kpiAvg: (c) => `Total Average ${c}`,
                kpiMin: (c) => `Min ${c}`,
                kpiMax: (c) => `Max ${c}`,
                chartDist: (c) => `${c} Distribution (Mock Bar Chart)`, chartTrend: (c) => `${c} Trend over Quarters (Mock Line Chart)`,
                explorerTitle: 'Data Explorer: Pivot & Visualization', explorerSubtitle: 'Use the controls below to configure your pivot table and view results instantly.',
                pivotTitle: 'Pivot Table Configuration', pivotRow: 'Row Field (Group By)', pivotCol: 'Column Field (Ignored in Simple Pivot)', pivotAggTypeLabel: 'Aggregation Type', pivotValueColLabel: 'Value Column',
                pivotSelectRow: '--- Select Row Field ---', pivotSelectCol: '--- Select Column Field (Optional) ---', pivotSelectAgg: '--- Select Aggregation Type ---', pivotSelectColAgg: '--- Select Value Column ---',
                pivotGenerate: 'Generate Pivot & Chart', pivotMockDefault: 'Select fields from the dropdowns above to view the results.',
                pivotMockNoFields: 'Please select Row Field, Aggregation Type, and Value Column.',
                pivotSelectAllFields: 'Please select a Row Field, Aggregation Type, and Value Column.',
                rawDataTitle: 'Raw Data Preview',
                emptyStateMsg: (t) => `${t} cannot be rendered without data.`, emptyStateInstruction: 'Please upload a file using the sidebar control to view this analysis.',
                languageToggle: 'Change Language:', langButton: 'العربية',
                agg: { sum: 'Sum', average: 'Average', count: 'Count', min: 'Minimum', max: 'Maximum' },
                statsTitle: 'Statistical Insights',
                statsSubtitle: 'Descriptive statistics for all numeric columns in your dataset.',
                statsTableTitle: 'Statistics Summary',
                statsHeaderMetric: 'Metric',
                statsCount: 'Count', statsMean: 'Mean', statsStdDev: 'Std. Dev.', statsMin: 'Min', statsMedian: 'Median', statsMax: 'Max',
                kpiSelectDefault: 'Select columns...', 
                kpiSelected: (c) => `${c} selected`
            },
            ar: {
                dir: 'rtl',
                pageTitle: 'المحلل الديناميكي', themeToggle: 'تبديل المظهر', dataSource: '📥 مصدر البيانات',
                statusNoData: 'لم يتم تحميل أي بيانات بعد. يرجى تحميل ملف.',
                statusLoaded: (r, c) => `✅ تم تحميل البيانات! (${r} صف، ${c} عمود)`,
                uploadLabel: 'تحميل البيانات (CSV/XLSX)', uploadNote: 'ملاحظة: ملفات CSV مدعومة بالكامل. XLSX تستخدم بيانات وهمية.',
                valueColLabel: 'أعمدة القيمة لمؤشرات الأداء', selectPage: 'اختيار الصفحة',
                navDashboard: 'لوحة القيادة', navStats: 'إحصائيات وتحليلات', navExplorer: 'مستكشف البيانات', navForecast: 'التنبؤ',
                dashboardTitle: 'لوحة القيادة الديناميكية',
                kpiTotalOrders: 'إجمالي الطلبات',
                kpiTotalCols: 'إجمالي الأعمدة',
                kpiTotal: (c) => `إجمالي ${c}`, 
                kpiAvg: (c) => `المتوسط الإجمالي ${c}`,
                kpiMin: (c) => `أدنى ${c}`,
                kpiMax: (c) => `أقصى ${c}`,
                chartDist: (c) => `توزيع ${c} (مخطط شريطي وهمي)`, chartTrend: (c) => `اتجاه ${c} عبر الأرباع (مخطط خطي وهمي)`,
                explorerTitle: 'مستكشف البيانات: المحور والتصور', explorerSubtitle: 'استخدم عناصر التحكم أدناه لتكوين جدولك المحوري وعرض النتائج على الفور.',
                pivotTitle: 'تكوين الجدول المحوري', pivotRow: 'حقل الصف (التجميع حسب)', pivotCol: 'حقل العمود (تم تجاهله في المحور البسيط)', pivotAggTypeLabel: 'نوع التجميع', pivotValueColLabel: 'عمود القيمة',
                pivotSelectRow: '--- اختر حقل الصف ---', pivotSelectCol: '--- اختر حقل العمود (اختياري) ---', pivotSelectAgg: '--- اختر نوع التجميع ---', pivotSelectColAgg: '--- اختر عمود القيمة ---',
                pivotGenerate: 'توليد المحور والمخطط', pivotMockDefault: 'اختر الحقول من القوائم المنسدلة أعلاه لعرض النتائج.',
                pivotMockNoFields: 'الرجاء تحديد حقل الصف، ونوع التجميع، وعمود القيمة.',
                pivotSelectAllFields: 'الرجاء تحديد حقل الصف، ونوع التجميع، وعمود القيمة.',
                rawDataTitle: 'معاينة البيانات الأولية',
                emptyStateMsg: (t) => `لا يمكن عرض ${t} بدون بيانات.`, emptyStateInstruction: 'يرجى تحميل ملف باستخدام عنصر التحكم في الشريط الجانبي لعرض هذا التحليل.',
                languageToggle: 'تغيير اللغة:', langButton: 'English',
                agg: { sum: 'المجموع', average: 'المتوسط', count: 'العدد', min: 'الحد الأدنى', max: 'الحد الأقصى' },
                statsTitle: 'إحصائيات وتحليلات',
                statsSubtitle: 'إحصائيات وصفية لجميع الأعمدة الرقمية في مجموعة البيانات الخاصة بك.',
                statsTableTitle: 'ملخص الإحصائيات',
                statsHeaderMetric: 'المقياس',
                statsCount: 'العدد', statsMean: 'المتوسط', statsStdDev: 'الانحراف المعياري', statsMin: 'الأدنى', statsMedian: 'الوسيط', statsMax: 'الأقصى',
                kpiSelectDefault: 'اختر الأعمدة...', 
                kpiSelected: (c) => `تم اختيار ${c}`
            },
        };

        // --- DOM Elements ---
        const contentDiv = document.getElementById('content');
        const navButtons = document.querySelectorAll('.nav-button');
        const dataUploadInput = document.getElementById('dataUpload');
        const valueColContainer = document.getElementById('valueColContainer');
        const kpiColSelectButton = document.getElementById('kpiColSelectButton');
        const kpiColSelectButtonText = document.getElementById('kpiColSelectButtonText');
        const kpiColumnPopover = document.getElementById('kpiColumnPopover');
        const body = document.body;
        
        // --- Utility Functions for Localization ---
        
        /** Translates internal header keys to user-facing display names based on current language. */
        function getHeaderDisplayName(header, lang = currentLang) {
            if (lang === 'ar') {
                switch (header) {
                    case 'Quarter': return 'الربع';
                    case 'Group': return 'المجموعة';
                    case 'Item_Tax_Rate': return 'ضريبة الصنف';
                    case 'Discounts': return 'الخصومات';
                    case 'Value_After_Tax_Discount': return 'قيمة بعد الضريبة و الخصم';
                    case 'Value_After_Tax': return 'قيمة بعد الضريبة';
                    case 'Value_Before_Tax_Discount': return 'قيمة قبل الضريبة و الخصم';
                    default: return header.replace(/_/g, ' ');
                }
            }
            return header.replace(/_/g, ' ');
        }

        /** Updates UI text based on the current language. */
        function updateUIText() {
            const t = translations[currentLang];

            // Update static elements
            document.getElementById('appTitle').textContent = t.pageTitle;
            document.getElementById('dataSourceTitle').textContent = t.dataSource;
            document.getElementById('uploadLabel').textContent = t.uploadLabel;
            document.getElementById('uploadNote').textContent = t.uploadNote;
            document.getElementById('valueColLabel').textContent = t.valueColLabel;
            document.getElementById('selectPageTitle').textContent = t.selectPage;
            document.getElementById('themeToggleText').textContent = t.themeToggle;
            document.getElementById('langToggleLabel').textContent = t.languageToggle;
            document.getElementById('langToggle').textContent = t.langButton;
            
            // Update nav buttons
            document.querySelectorAll('[data-text-key]').forEach(el => {
                const key = el.getAttribute('data-text-key');
                if (t[key]) el.textContent = t[key];
            });

            // Re-render data status and current page content
            updateDataStatus();
            populateKpiColumnSelector(); // Repopulate selectors with new localized names
            const activePage = document.querySelector('.nav-button.active')?.dataset.page || 'dashboard';
            navigateTo(activePage, true); // Silent refresh
        }

        /** Sets the application language and direction. */
        function setLanguage(lang) {
            currentLang = lang;
            body.dir = translations[lang].dir;
            updateUIText();
        }
        
        document.getElementById('langToggle').addEventListener('click', () => {
            setLanguage(currentLang === 'en' ? 'ar' : 'en');
        });

        // --- Other Utility Functions ---

        /** Shows a temporary notification message in the bottom right corner. */
        function showNotification(message, type = 'info') {
            const bar = document.getElementById('notificationBar');
            const msg = document.getElementById('notificationMessage');
            
            let baseClasses = "fixed bottom-4 p-4 rounded-xl shadow-2xl z-50 transition-transform duration-500";
            const dirClass = currentLang === 'ar' ? 'left-4' : 'right-4';
            
            if (type === 'success') {
                bar.className = baseClasses + " bg-green-500 text-white " + dirClass;
            } else if (type === 'error') {
                bar.className = baseClasses + " bg-red-500 text-white " + dirClass;
            } else if (type === 'warning') {
                bar.className = baseClasses + " bg-yellow-500 text-gray-900 " + dirClass;
            } else {
                bar.className = baseClasses + " bg-blue-500 text-white " + dirClass;
            }

            msg.textContent = message;
            bar.classList.remove('hidden', 'translate-x-full', 'translate-x-0', '-translate-x-full');
            
            // Reset visibility based on direction
            bar.classList.add(currentLang === 'ar' ? 'translate-x-full' : 'translate-x-full'); 
            
            setTimeout(() => {
                bar.classList.remove('translate-x-full', '-translate-x-full');
                bar.classList.add('translate-x-0');
            }, 50);


            setTimeout(() => {
                bar.classList.remove('translate-x-0');
                bar.classList.add(currentLang === 'ar' ? 'translate-x-full' : 'translate-x-full');
                setTimeout(() => { bar.classList.add('hidden'); }, 500);
            }, 4000);
        }

        /** Loads the hardcoded mock data for initial display. */
        function loadDefaultData() {
            appData = MOCK_XLSX_DATA;
            appHeaders = Object.keys(appData[0]);
            showNotification(currentLang === 'en' ? 'Data automatically loaded from mock source.' : 'تم تحميل البيانات تلقائيًا من مصدر وهمي.', 'info');
            updateDataStatus();
            populateKpiColumnSelector(); // Use new function
        }

        /** Updates the data status panel. */
        function updateDataStatus() {
            const statusDiv = document.getElementById('dataStatus');
            const t = translations[currentLang];

            if (appData.length > 0) {
                statusDiv.className = "p-3 rounded-xl text-sm border font-medium bg-green-100 border-green-200 text-green-800 dark:bg-green-900/50 dark:border-green-800 dark:text-green-300";
                statusDiv.innerHTML = t.statusLoaded(appData.length, appHeaders.length);
                valueColContainer.classList.remove('hidden');
            } else {
                statusDiv.className = "p-3 rounded-xl text-sm border font-medium bg-yellow-100 border-yellow-200 text-yellow-800 dark:bg-yellow-900/50 dark:border-yellow-800 dark:text-yellow-300";
                statusDiv.innerHTML = t.statusNoData;
                valueColContainer.classList.add('hidden');
            }
        }
        
        /** Populates the KPI Column multi-selector with numeric headers. */
        function populateKpiColumnSelector() {
            const t = translations[currentLang];
            kpiColumnPopover.innerHTML = ''; // Clear previous options
            
            numericHeadersCache = appHeaders.filter(h => {
                const sample = appData.find(row => row[h] != null && row[h] !== '');
                return sample && !isNaN(parseFloat(sample[h]));
            });
            
            // Set default selection if none exists or if data reloaded
            if (selectedKpiColumns.length === 0) {
                 let defaultHeader = numericHeadersCache.find(h => h === 'Value_After_Tax_Discount') || numericHeadersCache[0];
                 if (defaultHeader) {
                     selectedKpiColumns = [defaultHeader];
                 }
            }

            if (numericHeadersCache.length === 0) {
                kpiColumnPopover.innerHTML = `<span class="block p-2 text-sm text-gray-500">${currentLang === 'en' ? 'No numeric columns found' : 'لم يتم العثور على أعمدة رقمية'}</span>`;
            }

            numericHeadersCache.forEach(header => {
                const isChecked = selectedKpiColumns.includes(header);
                const id = `kpi-col-${header.replace(/[^a-zA-Z0-9]/g, '-')}`;
                
                const item = document.createElement('div');
                item.className = 'p-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer flex items-center';
                
                item.innerHTML = `
                    <input id="${id}" type="checkbox" ${isChecked ? 'checked' : ''} value="${header}" class="kpi-col-checkbox w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600 ${currentLang === 'ar' ? 'ml-2' : 'mr-2'}">
                    <label for="${id}" class="text-sm font-medium text-gray-900 dark:text-gray-300 cursor-pointer">${getHeaderDisplayName(header, currentLang)}</label>
                `;
                
                item.querySelector('input').addEventListener('change', (e) => {
                    const colName = e.target.value;
                    if (e.target.checked) {
                        if (!selectedKpiColumns.includes(colName)) {
                            selectedKpiColumns.push(colName);
                        }
                    } else {
                        selectedKpiColumns = selectedKpiColumns.filter(c => c !== colName);
                    }
                    updateKpiButtonText();
                    
                    // Refresh dashboard if currently active
                    if (document.querySelector('.nav-button.active')?.dataset.page === 'dashboard') {
                        navigateTo('dashboard', true); // Silent refresh
                    }
                });
                
                kpiColumnPopover.appendChild(item);
            });
            
            updateKpiButtonText();
            
            // Re-render the current page to apply new data/selection
            // navigateTo(document.querySelector('.nav-button.active')?.dataset.page || 'dashboard', true); // Silent navigation
        }
        
        /** Updates the text on the KPI selector button. */
        function updateKpiButtonText() {
            const t = translations[currentLang];
            if (selectedKpiColumns.length === 0) {
                kpiColSelectButtonText.textContent = t.kpiSelectDefault;
            } else {
                kpiColSelectButtonText.textContent = t.kpiSelected(selectedKpiColumns.length);
            }
        }


        // --- Data Analysis Functions (KPIs, Raw Data Table) ---

        /** Calculates KPIs based on the selected value columns, using current language. */
        function calculateKPIs(data, headers, selectedColumns) {
            const t = translations[currentLang];
            if (!data || data.length === 0) return [];
            
            let kpis = [
                { title: t.kpiTotalOrders, value: data.length.toLocaleString(), icon: "🔢" },
                { title: t.kpiTotalCols, value: headers.length.toLocaleString(), icon: "📊" },
            ];

            if (!selectedColumns || selectedColumns.length === 0) return kpis;
            
            selectedColumns.forEach(valueCol => {
                const displayColTitle = getHeaderDisplayName(valueCol, currentLang);
                const numericValues = data
                    .map(row => parseFloat(row[valueCol]))
                    .filter(v => !isNaN(v));

                const totalSum = numericValues.reduce((sum, v) => sum + v, 0);
                const avgValue = numericValues.length > 0 ? totalSum / numericValues.length : 0;
                const minValue = numericValues.length > 0 ? Math.min(...numericValues) : 0;
                const maxValue = numericValues.length > 0 ? Math.max(...numericValues) : 0;

                kpis.push(
                    { title: t.kpiTotal(displayColTitle), value: '$' + totalSum.toFixed(2).toLocaleString(), icon: "💰" },
                    { title: t.kpiAvg(displayColTitle), value: '$' + avgValue.toFixed(2).toLocaleString(), icon: "💸" },
                    { title: t.kpiMin(displayColTitle), value: '$' + minValue.toFixed(2).toLocaleString(), icon: "📉" },
                    { title: t.kpiMax(displayColTitle), value: '$' + maxValue.toFixed(2).toLocaleString(), icon: "📈" }
                );
            });

            return kpis;
        }
        
        /** Renders a reusable Raw Data Table component, showing ALL data. */
        function renderRawDataTable(data, headers, title) {
            const t = translations[currentLang];
            
            const displayData = data; 
            
            const tableRows = displayData.map(row => {
                const rowCells = headers.map(header => 
                    `<td class="p-3 border dark:border-gray-600 text-sm whitespace-nowrap">${row[header] || '-'}</td>`
                ).join('');
                return `<tr class="hover:bg-gray-50 dark:hover:bg-gray-700">${rowCells}</tr>`;
            }).join('');
            
            let noteText;
            if (data.length > 100) {
                noteText = currentLang === 'en' 
                    ? `Showing all ${data.length} records. (Note: Very large tables may impact performance).`
                    : `عرض جميع ${data.length} سجلات. (ملاحظة: قد تؤثر الجداول الكبيرة جدًا على الأداء).`;
            } else {
                noteText = currentLang === 'en' 
                    ? `Showing all ${data.length} records.`
                    : `عرض جميع ${data.length} سجلات.`;
            }
            
            return `
                <div class="metric-card p-6 rounded-2xl mt-8">
                    <h2 class="text-2xl font-bold mb-4 border-b pb-2 dark:border-gray-600">${title}</h2>
                    <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">${noteText}</p>
                    <div class="overflow-x-auto border rounded-xl shadow-lg dark:border-gray-700">
                        <table class="min-w-full text-left border-collapse">
                            <thead>
                                <tr class="bg-gray-200 dark:bg-gray-700/70 text-xs uppercase tracking-wider text-gray-600 dark:text-gray-300 sticky top-0">
                                    ${headers.map(header => `<th class="p-3 border dark:border-gray-600">${getHeaderDisplayName(header, currentLang)}</th>`).join('')}
                                </tr>
                            </thead>
                            <tbody>
                                ${tableRows}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        // --- Pivot Calculation Helpers ---

        /**
         * Formats a number based on aggregation type and current locale.
         */
        function formatPivotValue(value, aggType) {
            if (aggType === 'count') {
                return value.toLocaleString(currentLang);
            }
            // Use currency style for better visual representation of value data
            return new Intl.NumberFormat(currentLang === 'ar' ? 'ar-EG' : 'en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(value);
        }

        /**
         * Aggregates the data based on user selections.
         */
        function calculatePivot(rowField, aggType, valueField) {
            if (!rowField || !aggType || !valueField || appData.length === 0) return { data: {}, total: 0 };
            
            const pivoted = {};
            const numericData = appData.map(row => ({
                groupKey: row[rowField],
                value: parseFloat(row[valueField])
            }));

            // 1. Grouping
            const grouped = numericData.reduce((acc, { groupKey, value }) => {
                if (!acc[groupKey]) {
                    acc[groupKey] = [];
                }
                // Only push valid numbers for numeric aggregation
                if (aggType === 'count' || !isNaN(value)) {
                     acc[groupKey].push(aggType === 'count' ? 1 : value);
                }
                return acc;
            }, {});

            // 2. Aggregation
            for (const key in grouped) {
                const values = grouped[key];
                let result;

                switch (aggType) {
                    case 'sum':
                        result = values.reduce((s, v) => s + v, 0);
                        break;
                    case 'average':
                        result = values.length > 0 ? values.reduce((s, v) => s + v, 0) / values.length : 0;
                        break;
                    case 'min':
                        result = values.length > 0 ? Math.min(...values) : 0;
                        break;
                    case 'max':
                        result = values.length > 0 ? Math.max(...values) : 0;
                        break;
                    case 'count':
                        // Count is already done by values.length
                        result = values.length;
                        break;
                    default:
                        result = 0;
                }
                pivoted[key] = result;
            }
            
            const total = Object.values(pivoted).reduce((s, v) => s + v, 0);

            return { data: pivoted, total: total };
        }

        /**
         * Renders the HTML pivot table.
         */
        function renderPivotTable(pivotedData, rowField, aggType, valueField, total) {
            const container = document.getElementById('pivotTableContainer');
            const t = translations[currentLang];
            const rowDisplay = getHeaderDisplayName(rowField, currentLang);
            const aggDisplay = t.agg[aggType];
            const valueDisplay = getHeaderDisplayName(valueField, currentLang);

            if (Object.keys(pivotedData).length === 0) {
                container.innerHTML = `<p class="text-gray-500 text-center p-4">${t.pivotMockDefault}</p>`;
                return;
            }

            let html = `<div class="overflow-y-auto max-h-80"><table class="min-w-full text-sm border-collapse rounded-xl overflow-hidden">`;
            html += `<thead class="bg-blue-600 text-white sticky top-0"><tr>
                <th class="p-3">${rowDisplay}</th>
                <th class="p-3 text-right">${aggDisplay} of ${valueDisplay}</th>
            </tr></thead>`;
            html += `<tbody>`;

            for (const key in pivotedData) {
                const value = pivotedData[key];
                html += `<tr class="border-b dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700/50">
                    <td class="p-3 font-medium">${key}</td>
                    <td class="p-3 text-right">${formatPivotValue(value, aggType)}</td>
                </tr>`;
            }
            
            // Grand Total Row
            html += `<tfoot class="bg-gray-200 dark:bg-gray-700/80 font-bold border-t-2 border-blue-500 dark:border-blue-400"><tr>
                <td class="p-3">${currentLang === 'en' ? 'Grand Total' : 'الإجمالي الكلي'}</td>
                <td class="p-3 text-right text-lg text-blue-700 dark:text-blue-300">${formatPivotValue(total, aggType)}</td>
            </tr></tfoot>`;

            html += `</tbody></table></div>`;
            container.innerHTML = html;
        }

        /**
         * Renders or updates the Chart.js visualization.
         */
        function renderPivotChart(pivotedData, rowField, aggType, valueField) {
            const ctx = document.getElementById('pivotChart');
            const t = translations[currentLang];
            const labels = Object.keys(pivotedData);
            const values = Object.values(pivotedData);
            
            const rowDisplay = getHeaderDisplayName(rowField, currentLang);
            const aggDisplay = t.agg[aggType];
            const valueDisplay = getHeaderDisplayName(valueField, currentLang);
            
            if (myChart) {
                myChart.destroy();
            }
            
            let color = '#2563eb'; // Blue-600 default
            if (aggType === 'sum' || aggType === 'max') color = '#059669'; // Green-600
            if (aggType === 'average') color = '#f59e0b'; // Amber-600
            if (aggType === 'min') color = '#ef4444'; // Red-500
            
            myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: `${aggDisplay} of ${valueDisplay}`,
                        data: values,
                        backgroundColor: color,
                        borderRadius: 4,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top' },
                        title: {
                            display: true,
                            text: `${aggDisplay} of ${valueDisplay} by ${rowDisplay}`,
                            font: { size: 16, weight: 'bold' }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: `${aggDisplay} Value`
                            },
                            ticks: {
                                callback: function(value) {
                                     if (aggType === 'count') {
                                        return value.toLocaleString(currentLang);
                                    }
                                    return new Intl.NumberFormat(currentLang === 'ar' ? 'ar-EG' : 'en-US', {
                                        notation: 'compact', 
                                        minimumFractionDigits: 0,
                                        maximumFractionDigits: 1
                                    }).format(value);
                                }
                            }
                        }
                    }
                }
            });
        }
        
        // --- Page Renderers ---

        function renderEmptyState(title, message) {
            const t = translations[currentLang];
            return `
                <h1 class="text-3xl md:text-4xl font-extrabold mb-6 text-gray-800 dark:text-gray-100">${t.dashboardTitle || t.navDashboard}</h1>
                <div class="p-12 text-center border-4 border-dashed border-gray-300 dark:border-gray-700 rounded-2xl bg-gray-50 dark:bg-gray-800 mt-10">
                    <span class="text-6xl mb-4 block">🚫</span>
                    <p class="text-xl font-semibold text-gray-600 dark:text-gray-400">${t.emptyStateMsg(title)}</p>
                    <p class="text-lg text-gray-500 dark:text-gray-500 mt-2">${t.emptyStateInstruction}</p>
                </div>
            `;
        }

        function renderDashboard() {
            const t = translations[currentLang];
            if (appData.length === 0) {
                return renderEmptyState(t.navDashboard, t.navDashboard);
            }

            const kpis = calculateKPIs(appData, appHeaders, selectedKpiColumns);
            
            const displayColTitles = selectedKpiColumns.length > 0 
                ? selectedKpiColumns.map(col => getHeaderDisplayName(col, currentLang)).join(', ')
                : (currentLang === 'en' ? 'N/A' : 'لا يوجد');

            const chartCategoryCol = appHeaders.find(h => h === 'Quarter' || h === 'Group') || appHeaders[0];
            const chartCategoryDisplay = getHeaderDisplayName(chartCategoryCol, currentLang);
            
            // Destroy pivot chart when navigating away
            if (myChart) myChart.destroy();

            let html = `
                <h1 class="text-3xl md:text-4xl font-extrabold mb-6 text-gray-800 dark:text-gray-100">${t.dashboardTitle}</h1>
                <p class="text-gray-500 dark:text-gray-400 mb-8">${t.valueColLabel}: <span class="font-bold text-blue-500">${displayColTitles}</span>.</p>

                <!-- KPI Cards -->
                <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 mb-10">
                    ${kpis.map(kpi => `
                        <div class="metric-card p-5 rounded-2xl">
                            <div class="flex items-center">
                                <span class="text-3xl ${currentLang === 'ar' ? 'ml-3' : 'mr-3'}">${kpi.icon}</span>
                                <p class="text-lg font-semibold">${kpi.title}</p>
                            </div>
                            <p class="text-4xl font-bold mt-2 text-blue-600 dark:text-blue-400">${kpi.value}</p>
                        </div>
                    `).join('')}
                </div>

                <!-- Mock Visualizations -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- Chart 1: Categorical Distribution Mock -->
                    <div class="metric-card p-5 rounded-2xl">
                        <h2 class="text-xl font-bold mb-4 border-b pb-2 dark:border-gray-600">${t.chartDist(chartCategoryDisplay)}</h2>
                        <div class="h-64 bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-gray-600 dark:text-gray-400 rounded-xl border border-dashed border-gray-400 dark:border-gray-600">
                            <p>Placeholder: Bar chart showing count/sum across values in **${chartCategoryDisplay}**</p>
                        </div>
                    </div>

                    <!-- Chart 2: Time Series / Trend Mock -->
                    <div class="metric-card p-5 rounded-2xl">
                        <h2 class="text-xl font-bold mb-4 border-b pb-2 dark:border-gray-600">${t.chartTrend(displayColTitles)}</h2>
                        <div class="h-64 bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-gray-600 dark:text-gray-400 rounded-xl border border-dashed border-gray-400 dark:border-gray-600">
                            <p>Placeholder: Line chart showing total **${displayColTitles}** over Quarters</p>
                        </div>
                    </div>
                </div>
            `;
            
            // Raw data table added to the dashboard
            html += renderRawDataTable(appData, appHeaders, t.rawDataTitle);
            
            return html;
        }
        
        function createHeaderOptions(headers) {
            return headers.map(header => {
                const display = getHeaderDisplayName(header, currentLang);
                return `<option value="${header}">${display}</option>`;
            }).join('');
        }

        function renderDataExplorer() {
            const t = translations[currentLang];
            if (appData.length === 0) {
                return renderEmptyState(t.navExplorer, t.navExplorer);
            }
            
            const headerOptions = createHeaderOptions(appHeaders);
            
            // Destroy pivot chart on page render if it exists from a previous run
            if (myChart) myChart.destroy();

            return `
                <h1 class="text-3xl md:text-4xl font-extrabold mb-6 text-gray-800 dark:text-gray-100">${t.explorerTitle}</h1>
                <p class="text-gray-500 dark:text-gray-400 mb-8">${t.explorerSubtitle}</p>

                <!-- Pivot Controls -->
                <div class="metric-card p-6 rounded-2xl mb-8">
                    <h2 class="text-2xl font-bold mb-4 border-b pb-2 dark:border-gray-600">${t.pivotTitle}</h2>
                    <div id="pivotControls" class="flex flex-wrap items-center gap-6">
                        
                        <!-- Row Field -->
                        <div>
                            <label for="pivotRows" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">${t.pivotRow}</label>
                            <select id="pivotRows" class="w-48 p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 dark:text-gray-200 shadow-sm">
                                <option value="">${t.pivotSelectRow}</option>
                                ${headerOptions}
                            </select>
                        </div>

                        <!-- Column Field (Disabled) -->
                        <div>
                            <label for="pivotCols" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">${t.pivotCol}</label>
                            <select id="pivotCols" class="w-48 p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 dark:text-gray-200 shadow-sm" disabled>
                                <option value="">${t.pivotSelectCol}</option>
                                ${headerOptions}
                            </select>
                        </div>
                        
                        <!-- Aggregation Type -->
                        <div>
                            <label for="pivotAggType" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">${t.pivotAggTypeLabel}</label>
                            <select id="pivotAggType" class="w-48 p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 dark:text-gray-200 shadow-sm">
                                <option value="">${t.pivotSelectAgg}</option>
                                <option value="sum">${t.agg.sum}</option>
                                <option value="average">${t.agg.average}</option>
                                <option value="count">${t.agg.count}</option>
                                <option value="min">${t.agg.min}</option>
                                <option value="max">${t.agg.max}</option>
                            </select>
                        </div>
                        
                        <!-- Value Column -->
                        <div>
                            <label for="pivotValueColumn" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">${t.pivotValueColLabel}</label>
                            <select id="pivotValueColumn" class="w-48 p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 dark:text-gray-200 shadow-sm">
                                <option value="">${t.pivotSelectColAgg}</option>
                                ${createHeaderOptions(numericHeadersCache)}
                            </select>
                        </div>
                        
                    </div>

                </div>
                
                <!-- Pivot Output Grid -->
                <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
                    <!-- Chart -->
                    <div class="xl:col-span-2 metric-card p-6 rounded-2xl">
                        <h3 class="text-xl font-bold mb-4 border-b pb-2 dark:border-gray-600">Pivot Visualization</h3>
                        <div class="h-96 flex items-center justify-center">
                            <canvas id="pivotChart" class="w-full h-full"></canvas>
                        </div>
                    </div>
                    <!-- Table -->
                    <div class="xl:col-span-1 metric-card p-6 rounded-2xl">
                        <h3 class="text-xl font-bold mb-4 border-b pb-2 dark:border-gray-600">Pivot Table Output</h3>
                        <div id="pivotTableContainer" class="min-w-full">
                            <p class="text-gray-500 text-center p-4">${t.pivotMockDefault}</p>
                        </div>
                    </div>
                </div>
                
                <!-- Raw Data Table -->
                ${renderRawDataTable(appData, appHeaders, t.rawDataTitle)}
            `;
        }
        
        // --- Statistical Calculation Helpers ---
        function getMedian(arr) {
            if (!arr.length) return 0;
            const sorted = [...arr].sort((a, b) => a - b);
            const mid = Math.floor(sorted.length / 2);
            return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
        }

        function getStdDev(arr) {
            const n = arr.length;
            if (n < 2) return 0;
            const mean = arr.reduce((a, b) => a + b) / n;
            const variance = arr.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / (n - 1);
            return Math.sqrt(variance);
        }
        
        function calculateColumnStats(data, headers) {
            const numericHeaders = headers.filter(h => {
                const sample = data.find(row => row[h] != null && row[h] !== '');
                return sample && !isNaN(parseFloat(sample[h]));
            });

            return numericHeaders.map(header => {
                const values = data.map(row => parseFloat(row[header])).filter(v => !isNaN(v));
                const count = values.length;
                const sum = values.reduce((s, v) => s + v, 0);
                const mean = count > 0 ? sum / count : 0;
                
                return {
                    header: header,
                    count: count,
                    mean: mean,
                    stdDev: getStdDev(values),
                    min: count > 0 ? Math.min(...values) : 0,
                    median: getMedian(values),
                    max: count > 0 ? Math.max(...values) : 0,
                };
            });
        }
        
        function renderStats() {
            const t = translations[currentLang];
            if (appData.length === 0) {
                return renderEmptyState(t.navStats, t.navStats);
            }
            
            if (myChart) myChart.destroy();
            const statsData = calculateColumnStats(appData, appHeaders);

            const statRows = [
                { key: 'count', label: t.statsCount, format: (val) => val.toLocaleString(currentLang) },
                { key: 'mean', label: t.statsMean, format: (val) => val.toFixed(2) },
                { key: 'stdDev', label: t.statsStdDev, format: (val) => val.toFixed(2) },
                { key: 'min', label: t.statsMin, format: (val) => val.toFixed(2) },
                { key: 'median', label: t.statsMedian, format: (val) => val.toFixed(2) },
                { key: 'max', label: t.statsMax, format: (val) => val.toFixed(2) }
            ];

            return `
                <h1 class="text-3xl md:text-4xl font-extrabold mb-6 text-gray-800 dark:text-gray-100">${t.statsTitle}</h1>
                <p class="text-gray-500 dark:text-gray-400 mb-8">${t.statsSubtitle}</p>
                <div class="metric-card p-6 rounded-2xl">
                    <h2 class="text-2xl font-bold mb-4 border-b pb-2 dark:border-gray-600">${t.statsTableTitle}</h2>
                     <div class="overflow-x-auto border rounded-xl shadow-lg dark:border-gray-700">
                        <table class="min-w-full text-left text-sm">
                            <thead class="bg-gray-200 dark:bg-gray-700/70 text-xs uppercase tracking-wider text-gray-600 dark:text-gray-300">
                                <tr>
                                    <th class="p-3 font-semibold">${t.statsHeaderMetric}</th>
                                    ${statsData.map(col => `<th class="p-3 text-right font-semibold">${getHeaderDisplayName(col.header, currentLang)}</th>`).join('')}
                                </tr>
                            </thead>
                            <tbody>
                                ${statRows.map(row => `
                                    <tr class="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                                        <td class="p-3 font-medium">${row.label}</td>
                                        ${statsData.map(col => `<td class="p-3 text-right font-mono">${row.format(col[row.key])}</td>`).join('')}
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        function renderForecasting() {
            const t = translations[currentLang];
            if (appData.length === 0) {
                return renderEmptyState(t.navForecast, t.navForecast);
            }
            // Destroy pivot chart when navigating away
            if (myChart) myChart.destroy();
            
            return `
                <h1 class="text-3xl md:text-4xl font-extrabold mb-6 text-gray-800 dark:text-gray-100">${t.navForecast} and Future Demand</h1>
                <p class="text-gray-500 dark:text-gray-400 mb-8">Simulated demand forecasting based on your file.</p>

                <div class="metric-card p-5 rounded-2xl">
                    <h2 class="text-2xl font-bold mb-4 border-b pb-2 dark:border-gray-600">Forecasting Chart (Mock)</h2>
                    <div class="h-80 bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-gray-600 dark:text-gray-400 rounded-xl">
                        <p>Placeholder: Time series prediction using the **Quarter** column for dates.</p>
                    </div>
                </div>
            `;
        }
        
        const pageRenderers = {
            dashboard: renderDashboard,
            stats: renderStats,
            dataExplorer: renderDataExplorer,
            forecasting: renderForecasting
        };

        // --- Navigation and Listener Attachment ---

        function attachDataExplorerListeners() {
            const pivotTableContainer = document.getElementById('pivotTableContainer');
            const pivotRows = document.getElementById('pivotRows');
            const pivotAggType = document.getElementById('pivotAggType'); 
            const pivotValueColumn = document.getElementById('pivotValueColumn'); 
            const t = translations[currentLang];

            function generateAndUpdatePivot() {
                if (!pivotRows || !pivotAggType || !pivotValueColumn) return;
                
                const rowField = pivotRows.value;
                const aggType = pivotAggType.value;
                const valueField = pivotValueColumn.value;

                if (!rowField || !aggType || !valueField) {
                    pivotTableContainer.innerHTML = `<p class="p-4 text-yellow-600 dark:text-yellow-400 font-bold text-center">${t.pivotSelectAllFields}</p>`;
                    // Destroy chart if it exists and selections are incomplete
                    if (myChart) myChart.destroy();
                    return;
                }
                
                const { data: pivotedData, total } = calculatePivot(rowField, aggType, valueField);
                
                // Render the Table
                renderPivotTable(pivotedData, rowField, aggType, valueField, total);
                
                // Render the Chart
                renderPivotChart(pivotedData, rowField, aggType, valueField);
            }

            // Attach 'change' event listeners to all dropdowns
            if(pivotRows) pivotRows.addEventListener('change', generateAndUpdatePivot);
            if(pivotAggType) pivotAggType.addEventListener('change', generateAndUpdatePivot);
            if(pivotValueColumn) pivotValueColumn.addEventListener('change', generateAndUpdatePivot);
        }


        function navigateTo(page, silent = false) {
            if (!silent) {
                // Apply fade-out effect
                contentDiv.style.opacity = '0';
            }
            
            // Wait for fade-out, then change content and fade in
            setTimeout(() => {
                const renderer = pageRenderers[page] || renderDashboard;
                contentDiv.innerHTML = renderer();
                
                // --- Post-Render Logic ---
                if (page === 'dataExplorer') {
                    attachDataExplorerListeners();
                }
                
                // Update active button only if not silent
                if (!silent) {
                    navButtons.forEach(btn => {
                        btn.classList.remove('bg-blue-500', 'text-white', 'dark:bg-blue-600', 'active');
                        btn.classList.add('text-gray-700', 'dark:text-gray-200', 'hover:bg-gray-200', 'dark:hover:bg-gray-700');
                    });
                    
                    const activeButton = document.querySelector(`.nav-button[data-page="${page}"]`);
                    if (activeButton) {
                        activeButton.classList.add('bg-blue-500', 'text-white', 'dark:bg-blue-600', 'active');
                        activeButton.classList.remove('text-gray-700', 'dark:text-gray-200', 'hover:bg-gray-200', 'dark:hover:bg-gray-700');
                    }
                }
                
                // Apply fade-in effect
                contentDiv.style.opacity = '1';
            }, silent ? 0 : 300);
        }

        // --- Theme Toggle Logic ---
        const themeToggle = document.getElementById('themeToggle');
        const sunIcon = document.getElementById('sunIcon');
        const moonIcon = document.getElementById('moonIcon');

        function updateThemeIcons(isDark) {
            if (isDark) {
                moonIcon.classList.remove('hidden');
                sunIcon.classList.add('hidden');
            } else {
                moonIcon.classList.add('hidden');
                sunIcon.classList.remove('hidden');
            }
        }

        function setInitialTheme() {
            const isDark = localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
            
            if (isDark) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
            updateThemeIcons(isDark);
        }
        
        themeToggle.addEventListener('click', () => {
            const isDark = document.documentElement.classList.toggle('dark');
            localStorage.theme = isDark ? 'dark' : 'light';
            updateThemeIcons(isDark);
        });
        
        // --- File Upload Handler ---
        function handleFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            appData = [];
            appHeaders = [];
            selectedKpiColumns = []; // Reset selections on new file
            
            if (file.name.endsWith('.csv')) {
                Papa.parse(file, {
                    header: true, dynamicTyping: false, skipEmptyLines: true,
                    complete: function(results) {
                        const cleanHeaders = results.meta.fields.filter(h => h && h.trim() !== '');
                        appHeaders = cleanHeaders;
                        
                        appData = results.data
                            .filter(row => Object.values(row).some(v => v !== null && v !== ''))
                            .map(row => {
                                const newRow = {};
                                cleanHeaders.forEach(h => { newRow[h] = row[h] ? row[h].trim() : ''; });
                                return newRow;
                            });

                        if (appData.length === 0 || appHeaders.length === 0) {
                            showNotification(currentLang === 'en' ? "File uploaded but contains no valid data or headers." : "تم تحميل الملف ولكن لا يحتوي على بيانات أو رؤوس صالحة.", 'error');
                            updateDataStatus();
                            return;
                        }
                        
                        showNotification(currentLang === 'en' ? `Successfully loaded ${appData.length} rows from CSV.` : `تم تحميل ${appData.length} صف من ملف CSV بنجاخ.`, 'success');
                        updateDataStatus();
                        populateKpiColumnSelector();
                        navigateTo('dashboard');
                    },
                    error: function(err) {
                        showNotification(`Error parsing CSV: ${err.message}`, 'error');
                        updateDataStatus();
                    }
                });
            } else if (file.name.endsWith('.xlsx')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    try {
                        const data = new Uint8Array(e.target.result);
                        const workbook = XLSX.read(data, {type: 'array'});
                        const firstSheetName = workbook.SheetNames[0];
                        const worksheet = workbook.Sheets[firstSheetName];
                        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

                        if (jsonData.length < 2) {
                             showNotification(currentLang === 'en' ? "XLSX file is empty or has only headers." : "ملف XLSX فارغ أو يحتوي على رؤوس فقط.", 'error');
                            updateDataStatus();
                            return;
                        }

                        const headers = jsonData[0].map(String);
                        const rows = jsonData.slice(1);

                        appHeaders = headers;
                        appData = rows.map(rowArray => {
                            let obj = {};
                            headers.forEach((header, index) => {
                                obj[header] = rowArray[index] || '';
                            });
                            return obj;
                        });

                        showNotification(currentLang === 'en' ? `Successfully loaded ${appData.length} rows from XLSX.` : `تم تحميل ${appData.length} صف من ملف XLSX بنجاC.`, 'success');
                        updateDataStatus();
                        populateKpiColumnSelector();
                        navigateTo('dashboard');
                    } catch (err) {
                         showNotification(`Error parsing XLSX: ${err.message}`, 'error');
                         updateDataStatus();
                    }
                };
                reader.onerror = function() {
                    showNotification('Error reading file.', 'error');
                    updateDataStatus();
                };
                reader.readAsArrayBuffer(file);
            } else {
                showNotification(currentLang === 'en' ? "Please select a valid CSV or XLSX file." : "الرجاء اختيار ملف CSV أو XLSX صالح.", 'error');
            }
        }

        // --- Initialization ---
        
        // Event Listeners for Navigation
        navButtons.forEach(button => {
            button.addEventListener('click', () => {
                const page = button.getAttribute('data-page');
                navigateTo(page);
            });
        });

        // Event Listener for File Upload
        dataUploadInput.addEventListener('change', handleFileUpload);
        
        // --- KPI Column Selector Listeners ---
        kpiColSelectButton.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent click-outside from firing
            kpiColumnPopover.classList.toggle('hidden');
        });

        document.addEventListener('click', (e) => {
            if (!kpiColSelectButton.contains(e.target) && !kpiColumnPopover.contains(e.target)) {
                kpiColumnPopover.classList.add('hidden');
            }
        });

        // Load default page on startup and set theme
        setInitialTheme();
        loadDefaultData(); // Load the data immediately upon launch
        setLanguage('en'); // Start in English
    </script>
</body>
</html>


