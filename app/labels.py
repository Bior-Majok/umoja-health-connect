"""UI microcopy translations (NFR11 i18n framework).

English is authoritative. French and Swahili are direct translations of short UI
labels (not medical content, so no clinical vetting is required). Arabic includes
`dir: rtl` metadata consumed by the frontend to flip layout direction.

Health-education *content* (medical articles) is a separate concern — see
HealthEducationArticle.is_verified, which tracks whether a qualified reviewer has
signed off on the medical accuracy of translated content, per the SRS business rule.
"""

LANGUAGES = ['en', 'fr', 'sw', 'ar']
RTL_LANGUAGES = ['ar']

LABELS = {
    'login': {'en': 'Login', 'fr': 'Connexion', 'sw': 'Ingia', 'ar': 'تسجيل الدخول'},
    'register': {'en': 'Register', 'fr': "S'inscrire", 'sw': 'Jisajili', 'ar': 'تسجيل'},
    'logout': {'en': 'Log out', 'fr': 'Déconnexion', 'sw': 'Toka', 'ar': 'تسجيل الخروج'},
    'dashboard': {'en': 'Dashboard', 'fr': 'Tableau de bord', 'sw': 'Dashibodi', 'ar': 'لوحة التحكم'},
    'appointments': {'en': 'Appointments', 'fr': 'Rendez-vous', 'sw': 'Miadi', 'ar': 'المواعيد'},
    'medical_records': {'en': 'Medical Records', 'fr': 'Dossiers médicaux', 'sw': 'Rekodi za Afya', 'ar': 'السجلات الطبية'},
    'health_education': {'en': 'Health Education', 'fr': 'Éducation à la santé', 'sw': 'Elimu ya Afya', 'ar': 'التثقيف الصحي'},
    'emergency': {'en': 'Emergency', 'fr': 'Urgence', 'sw': 'Dharura', 'ar': 'طوارئ'},
    'book_appointment': {'en': 'Book Appointment', 'fr': 'Prendre un rendez-vous', 'sw': 'Weka Miadi', 'ar': 'حجز موعد'},
    'new_appointment': {'en': '+ New appointment', 'fr': '+ Nouveau rendez-vous', 'sw': '+ Miadi mpya', 'ar': '+ موعد جديد'},
    'add_record': {'en': '+ Add record', 'fr': '+ Ajouter un dossier', 'sw': '+ Ongeza rekodi', 'ar': '+ إضافة سجل'},
    'full_name': {'en': 'Full name', 'fr': 'Nom complet', 'sw': 'Jina kamili', 'ar': 'الاسم الكامل'},
    'phone_number': {'en': 'Phone number', 'fr': 'Numéro de téléphone', 'sw': 'Nambari ya simu', 'ar': 'رقم الهاتف'},
    'password': {'en': 'Password', 'fr': 'Mot de passe', 'sw': 'Nenosiri', 'ar': 'كلمة المرور'},
    'age': {'en': 'Age', 'fr': 'Âge', 'sw': 'Umri', 'ar': 'العمر'},
    'gender': {'en': 'Gender', 'fr': 'Genre', 'sw': 'Jinsia', 'ar': 'الجنس'},
    'country': {'en': 'Country', 'fr': 'Pays', 'sw': 'Nchi', 'ar': 'الدولة'},
    'region': {'en': 'Region', 'fr': 'Région', 'sw': 'Mkoa', 'ar': 'المنطقة'},
    'submit': {'en': 'Submit', 'fr': 'Soumettre', 'sw': 'Wasilisha', 'ar': 'إرسال'},
    'cancel': {'en': 'Cancel', 'fr': 'Annuler', 'sw': 'Ghairi', 'ar': 'إلغاء'},
    'save': {'en': 'Save', 'fr': 'Enregistrer', 'sw': 'Hifadhi', 'ar': 'حفظ'},
    'loading': {'en': 'Loading...', 'fr': 'Chargement...', 'sw': 'Inapakia...', 'ar': 'جارٍ التحميل...'},
    'welcome': {'en': 'Welcome', 'fr': 'Bienvenue', 'sw': 'Karibu', 'ar': 'مرحباً'},
    'profile': {'en': 'Profile', 'fr': 'Profil', 'sw': 'Wasifu', 'ar': 'الملف الشخصي'},
    'edit_profile': {'en': 'Edit profile', 'fr': 'Modifier le profil', 'sw': 'Hariri wasifu', 'ar': 'تعديل الملف الشخصي'},
    'symptoms': {'en': 'Symptoms', 'fr': 'Symptômes', 'sw': 'Dalili', 'ar': 'الأعراض'},
    'report_symptoms': {'en': 'Report symptoms', 'fr': 'Signaler des symptômes', 'sw': 'Ripoti dalili', 'ar': 'الإبلاغ عن الأعراض'},
    'consultation': {'en': 'Consultation', 'fr': 'Consultation', 'sw': 'Ushauri', 'ar': 'استشارة'},
    'date_time': {'en': 'Date & time', 'fr': 'Date et heure', 'sw': 'Tarehe na wakati', 'ar': 'التاريخ والوقت'},
    'notes': {'en': 'Notes', 'fr': 'Remarques', 'sw': 'Maelezo', 'ar': 'ملاحظات'},
    'doctor': {'en': 'Doctor', 'fr': 'Médecin', 'sw': 'Daktari', 'ar': 'طبيب'},
    'clinic': {'en': 'Clinic', 'fr': 'Clinique', 'sw': 'Kliniki', 'ar': 'عيادة'},
    'status': {'en': 'Status', 'fr': 'Statut', 'sw': 'Hali', 'ar': 'الحالة'},
    'upcoming': {'en': 'Upcoming', 'fr': 'À venir', 'sw': 'Ijayo', 'ar': 'قادم'},
    'completed': {'en': 'Completed', 'fr': 'Terminé', 'sw': 'Imekamilika', 'ar': 'مكتمل'},
    'cancelled': {'en': 'Cancelled', 'fr': 'Annulé', 'sw': 'Imeghairiwa', 'ar': 'ملغى'},
    'normal': {'en': 'Normal', 'fr': 'Normal', 'sw': 'Kawaida', 'ar': 'طبيعي'},
    'flagged': {'en': 'Flagged', 'fr': 'Signalé', 'sw': 'Imebainishwa', 'ar': 'محدد'},
    'home': {'en': 'Home', 'fr': 'Accueil', 'sw': 'Nyumbani', 'ar': 'الرئيسية'},
    'get_started': {'en': 'Get Started', 'fr': 'Commencer', 'sw': 'Anza', 'ar': 'ابدأ'},
    'language': {'en': 'Language', 'fr': 'Langue', 'sw': 'Lugha', 'ar': 'اللغة'},
    'family_contact': {'en': 'Family contact', 'fr': 'Contact familial', 'sw': 'Mawasiliano ya familia', 'ar': 'جهة اتصال العائلة'},

    'login_heading': {'en': 'Log in to your account', 'fr': 'Connectez-vous à votre compte', 'sw': 'Ingia kwenye akaunti yako', 'ar': 'سجّل الدخول إلى حسابك'},
    'register_heading': {'en': 'Create your account', 'fr': 'Créez votre compte', 'sw': 'Fungua akaunti yako', 'ar': 'أنشئ حسابك'},
    'no_account': {'en': "Don't have an account?", 'fr': "Vous n'avez pas de compte ?", 'sw': 'Huna akaunti?', 'ar': 'ليس لديك حساب؟'},
    'have_account': {'en': 'Already have an account?', 'fr': 'Vous avez déjà un compte ?', 'sw': 'Una akaunti tayari?', 'ar': 'هل لديك حساب بالفعل؟'},
    'register_here': {'en': 'Register here', 'fr': "S'inscrire ici", 'sw': 'Jisajili hapa', 'ar': 'سجّل هنا'},
    'log_in_link': {'en': 'Log in', 'fr': 'Connexion', 'sw': 'Ingia', 'ar': 'تسجيل الدخول'},
    'welcome_back': {'en': 'Welcome back', 'fr': 'Content de vous revoir', 'sw': 'Karibu tena', 'ar': 'مرحباً بعودتك'},
    'care_today': {'en': "Here's what's happening with your care today.", 'fr': "Voici ce qui se passe avec vos soins aujourd'hui.", 'sw': 'Haya ndiyo yanayoendelea na huduma yako ya afya leo.', 'ar': 'إليك آخر مستجدات رعايتك الصحية اليوم.'},
    'upcoming_appointments': {'en': 'Upcoming appointments', 'fr': 'Rendez-vous à venir', 'sw': 'Miadi ijayo', 'ar': 'المواعيد القادمة'},
    'active_consultations': {'en': 'Active consultations', 'fr': 'Consultations en cours', 'sw': 'Ushauri unaoendelea', 'ar': 'الاستشارات النشطة'},
    'your_appointments': {'en': 'Your appointments', 'fr': 'Vos rendez-vous', 'sw': 'Miadi yako', 'ar': 'مواعيدك'},
    'book_appointment_desc': {'en': 'Schedule with a provider', 'fr': 'Planifier avec un professionnel', 'sw': 'Panga na mtoa huduma', 'ar': 'حدد موعدًا مع مقدم رعاية'},
    'report_symptoms_desc': {'en': 'Get matched to a provider', 'fr': 'Soyez mis en relation avec un professionnel', 'sw': 'Utaunganishwa na mtoa huduma', 'ar': 'سيتم ربطك بمقدم رعاية'},
    'medical_records_desc': {'en': 'View your health history', 'fr': 'Consultez votre historique de santé', 'sw': 'Angalia historia yako ya afya', 'ar': 'اطّلع على سجلك الصحي'},
    'health_education_desc': {'en': 'Learn in your language', 'fr': 'Apprenez dans votre langue', 'sw': 'Jifunze kwa lugha yako', 'ar': 'تعلّم بلغتك'},
    'emergency_desc': {'en': 'Notify nearby providers now', 'fr': 'Alertez les professionnels à proximité', 'sw': 'Arifu watoa huduma walio karibu sasa', 'ar': 'أبلغ مقدمي الرعاية القريبين الآن'},
    'meet_providers': {'en': 'Meet our healthcare providers', 'fr': 'Découvrez nos professionnels de santé', 'sw': 'Kutana na watoa huduma wetu wa afya', 'ar': 'تعرّف على مقدمي الرعاية الصحية لدينا'},
    'save_changes': {'en': 'Save changes', 'fr': 'Enregistrer les modifications', 'sw': 'Hifadhi mabadiliko', 'ar': 'حفظ التغييرات'},
    'family_contact_optional': {'en': 'Family contact phone (optional)', 'fr': 'Téléphone du contact familial (facultatif)', 'sw': 'Simu ya mawasiliano ya familia (hiari)', 'ar': 'هاتف جهة اتصال العائلة (اختياري)'},
    'download_offline': {'en': 'Download for offline', 'fr': 'Télécharger pour usage hors ligne', 'sw': 'Pakua kwa matumizi nje ya mtandao', 'ar': 'تنزيل للاستخدام دون اتصال'},
    'health_ed_heading': {'en': 'Health education library', 'fr': 'Bibliothèque d’éducation à la santé', 'sw': 'Maktaba ya elimu ya afya', 'ar': 'مكتبة التثقيف الصحي'},
    'symptom_report_heading': {'en': 'Report your symptoms', 'fr': 'Signalez vos symptômes', 'sw': 'Ripoti dalili zako', 'ar': 'أبلغ عن أعراضك'},
    'symptom_report_desc': {'en': "Choose everything that applies, and add anything else in your own words. A verified healthcare provider will be assigned to your case automatically.", 'fr': "Sélectionnez tout ce qui s'applique et ajoutez toute autre précision dans vos propres mots. Un professionnel de santé vérifié sera automatiquement assigné à votre dossier.", 'sw': 'Chagua kila kinachohusika, kisha ongeza maelezo mengine kwa maneno yako. Mtoa huduma aliyethibitishwa atapangiwa kesi yako moja kwa moja.', 'ar': 'اختر كل ما ينطبق، وأضف أي تفاصيل أخرى بكلماتك. سيتم تعيين مقدم رعاية موثّق لحالتك تلقائيًا.'},
    'your_consultations': {'en': 'Your consultations', 'fr': 'Vos consultations', 'sw': 'Ushauri wako', 'ar': 'استشاراتك'},
    'describe_own_words': {'en': 'Describe in your own words (optional)', 'fr': 'Décrivez avec vos propres mots (facultatif)', 'sw': 'Eleza kwa maneno yako (hiari)', 'ar': 'صف الأمر بكلماتك (اختياري)'},
    'submit_report': {'en': 'Submit report', 'fr': 'Envoyer le rapport', 'sw': 'Wasilisha ripoti', 'ar': 'إرسال التقرير'},
    'cancel_and_back': {'en': 'Cancel and go back', 'fr': 'Annuler et revenir', 'sw': 'Ghairi na urudi', 'ar': 'إلغاء والعودة'},
    'title_field': {'en': 'Title', 'fr': 'Titre', 'sw': 'Kichwa', 'ar': 'العنوان'},
    'details_optional': {'en': 'Details (optional)', 'fr': 'Détails (facultatif)', 'sw': 'Maelezo (hiari)', 'ar': 'التفاصيل (اختياري)'},
    'date_recorded': {'en': 'Date recorded', 'fr': "Date d'enregistrement", 'sw': 'Tarehe ya kurekodiwa', 'ar': 'تاريخ التسجيل'},
    'provider_field': {'en': 'Provider', 'fr': 'Professionnel de santé', 'sw': 'Mtoa huduma', 'ar': 'مقدم الرعاية'},
    'save_record': {'en': 'Save record', 'fr': 'Enregistrer le dossier', 'sw': 'Hifadhi rekodi', 'ar': 'حفظ السجل'},
    'book_appointment_btn': {'en': 'Book appointment', 'fr': 'Prendre rendez-vous', 'sw': 'Weka miadi', 'ar': 'حجز موعد'},
    'book_appointment_heading': {'en': 'Book an appointment', 'fr': 'Prendre un rendez-vous', 'sw': 'Weka miadi', 'ar': 'حجز موعد'},
    'add_record_heading': {'en': 'Add a medical record', 'fr': 'Ajouter un dossier médical', 'sw': 'Ongeza rekodi ya afya', 'ar': 'إضافة سجل طبي'},

    'tagline': {'en': 'Healthcare made easy, anywhere', 'fr': 'Les soins de santé simplifiés, partout', 'sw': 'Huduma ya afya iliyorahisishwa, popote', 'ar': 'رعاية صحية سهلة، في أي مكان'},
    'hero_lede': {'en': 'Connect with verified healthcare providers, report symptoms, book appointments, and trigger emergency alerts — over the internet or plain SMS, no smartphone required.', 'fr': "Contactez des professionnels de santé vérifiés, signalez vos symptômes, prenez rendez-vous et déclenchez des alertes d'urgence — via Internet ou simple SMS, sans smartphone requis.", 'sw': 'Wasiliana na watoa huduma za afya waliothibitishwa, ripoti dalili, weka miadi, na tuma tahadhari za dharura — kupitia intaneti au SMS ya kawaida, hakuna simu janja inayohitajika.', 'ar': 'تواصل مع مقدمي رعاية صحية موثّقين، أبلغ عن الأعراض، احجز المواعيد، وأطلق تنبيهات الطوارئ — عبر الإنترنت أو الرسائل النصية القصيرة فقط، دون الحاجة لهاتف ذكي.'},
    'bullet_sms': {'en': 'SMS & mobile access, even offline', 'fr': 'Accès SMS et mobile, même hors ligne', 'sw': 'Ufikiaji wa SMS na simu, hata bila mtandao', 'ar': 'وصول عبر الرسائل النصية والجوال، حتى بلا اتصال'},
    'bullet_providers': {'en': 'Qualified, verified healthcare providers', 'fr': 'Professionnels de santé qualifiés et vérifiés', 'sw': 'Watoa huduma waliohitimu na kuthibitishwa', 'ar': 'مقدمو رعاية صحية مؤهلون وموثّقون'},
    'bullet_emergency': {'en': 'One-tap emergency alerts', 'fr': "Alertes d'urgence en un clic", 'sw': 'Tahadhari za dharura kwa mguso mmoja', 'ar': 'تنبيهات طوارئ بلمسة واحدة'},
    'bullet_communities': {'en': 'Built for low-resource African communities', 'fr': 'Conçu pour les communautés africaines à faibles ressources', 'sw': 'Imeundwa kwa jamii za Kiafrika zenye rasilimali chache', 'ar': 'مصمم للمجتمعات الأفريقية محدودة الموارد'},

    'symptom_fever': {'en': 'Fever', 'fr': 'Fièvre', 'sw': 'Homa', 'ar': 'حمى'},
    'symptom_cough': {'en': 'Cough', 'fr': 'Toux', 'sw': 'Kikohozi', 'ar': 'سعال'},
    'symptom_headache': {'en': 'Headache', 'fr': 'Mal de tête', 'sw': 'Maumivu ya kichwa', 'ar': 'صداع'},
    'symptom_diarrhea': {'en': 'Diarrhea', 'fr': 'Diarrhée', 'sw': 'Kuhara', 'ar': 'إسهال'},
    'symptom_vomiting': {'en': 'Vomiting', 'fr': 'Vomissements', 'sw': 'Kutapika', 'ar': 'قيء'},
    'symptom_bodyaches': {'en': 'Body aches', 'fr': 'Douleurs corporelles', 'sw': 'Maumivu ya mwili', 'ar': 'آلام في الجسم'},
    'symptom_breathing': {'en': 'Difficulty breathing', 'fr': 'Difficulté à respirer', 'sw': 'Ugumu wa kupumua', 'ar': 'صعوبة في التنفس'},
    'symptom_rash': {'en': 'Rash', 'fr': 'Éruption cutanée', 'sw': 'Upele', 'ar': 'طفح جلدي'},
    'symptom_bleeding': {'en': 'Bleeding', 'fr': 'Saignement', 'sw': 'Kutokwa na damu', 'ar': 'نزيف'},
    'symptom_fatigue': {'en': 'Fatigue', 'fr': 'Fatigue', 'sw': 'Uchovu', 'ar': 'إرهاق'},
}


def labels_for(lang):
    lang = lang if lang in LANGUAGES else 'en'
    return {
        'language': lang,
        'dir': 'rtl' if lang in RTL_LANGUAGES else 'ltr',
        'labels': {key: values.get(lang, values['en']) for key, values in LABELS.items()},
    }
