class AppConstants {
  static const String appName = 'JobHunter AI';
  static const String appVersion = '1.0.0';
  static const String apiBaseUrl = 'http://localhost:8000/api/v1';

  static const List<String> supportedPortals = [
    'Todos',
    'LinkedIn',
    'InfoJobs',
    'Tecnoempleo',
    'Indeed',
    'SEPE',
    'EURES',
    'Domestika',
    'Autonómicos',
  ];

  static const List<String> modalities = [
    'Todas',
    'Remoto',
    'Híbrido',
    'Presencial',
  ];

  static const List<String> spanishRegions = [
    'Todas las CCAA',
    'Madrid',
    'Cataluña',
    'Andalucía',
    'Comunidad Valenciana',
    'País Vasco',
    'Galicia',
    'Castilla y León',
    'Canarias',
    'Castilla-La Mancha',
    'Murcia',
    'Aragón',
    'Islas Baleares',
    'Extremadura',
    'Asturias',
    'Navarra',
    'Cantabria',
    'La Rioja',
    'Ceuta',
    'Melilla',
  ];

  static const List<String> crmStages = [
    'SAVED',
    'REVIEWING',
    'APPLIED',
    'INTERVIEW',
    'OFFER',
    'REJECTED',
  ];

  static const double mobileBreakpoint = 680.0;
  static const double tabletBreakpoint = 1080.0;
}
