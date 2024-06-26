export const getMyHarvardCourseInfo = async () => {
  const res = await (await fetch('https://portal.my.harvard.edu/psp/hrvihprd/EMPLOYEE/HRMS/s/WEBLIB_IS_DS.ISCRIPT1.FieldFormula.IScript_DrawSection?group=IS_SSS_SUMMARY_VIEW&section=SUMMARY_ALL')).text();
  const doc = new DOMParser().parseFromString(res, 'text/html');
  const courseMap = (div: Element, cart='Cart') => {
    const cartName = (div.querySelector('h2')?.textContent as string).split(' - ')[1];
    const cartClasses = Array.from(div.querySelectorAll('tr:not(.isSSS_ShopCartNonPrim)')).slice(1).map(tr => {
      const title = (
        tr.querySelector(`[headers="tbl${cart}_Course"] .isSSS_CourseTitle`)?.textContent ||
        tr.querySelector(`[headers="tbl${cart}_Course"] a`)?.textContent
      )?.replaceAll('  ', ' ') as string;
      const session = tr.querySelector(`[headers="tbl${cart}_Session"]`)?.textContent as string;
      const instructor = tr.querySelector(`[headers="tbl${cart}_Instructor"]`)?.textContent as string;
      const location = tr.querySelector(`[headers="tbl${cart}_Location"]`)?.textContent as string;
      const time = tr.querySelector(`[headers="tbl${cart}_Time"]`)?.textContent as string;
      const day = tr.querySelector(`[headers="tbl${cart}_Day"]`)?.textContent as string;
      return { title, session, instructor, location, time, day };
    }).filter(item => item.title);
    return { cartName, cartClasses };
  };
  const cartTerms = Array.from(doc.querySelectorAll('.isSSS_ShCtTermWrp:not(.huSSS_EnrollmentEvents)')).map(item => courseMap(item, 'Cart'));
  const enrolledTerms = Array.from(doc.querySelectorAll('.isSSS_ShCtSchWrp')).map(item => courseMap(item, ''));
  const terms = cartTerms.map((term, i) => ({ ...term, enrolledCourses: enrolledTerms[i].cartClasses }));
  return terms;
};

interface RequirementDetail {
  Requirement: string;
  RequirementLine: string;
  RequirementLineDate: string;
  RequirementStatus: string;
  AcademicProgram: string;
  AcademicPlan: string;
  RequirementSAA_Descr80: string;
  RequirementLineDescr80: string;
  RequirementStatusDescr: string;
  RequirementStatusTooltip: string;
  HasSearchText?: string;
  SearchText?: string;
}

interface RequirementGroup {
  RequirementGroup: string;
  RequirementGroupDate: string;
  RequirementGroupDescr: string;
  RequirementGroupSAA_Descr80: string;
  RequirementGroupDescrLong: string;
  Requirements: RequirementDetail[];
}

interface Config {
  StudentId: string;
  Institution: string;
  AcadCareer: string;
  AdvisorView: boolean;
  StudentName: string;
  AnalysisDB_Seq: number;
  ReportType: string;
  FlagCoursesTaken: boolean;
}

interface DebugInfo {
  numRows_SAA_ARSLT_RGVW: number;
  numRows_HU_SAARSLT_RLVW: number;
}

interface AcademicRecord {
  Config: Config;
  Results: RequirementGroup[];
  Debug: DebugInfo;
}


export const getMyHarvardRequirements = async (): Promise<AcademicRecord> => {
  const res = await (await fetch('https://portal.my.harvard.edu/psp/hrvihprd/EMPLOYEE/EMPL/s/WEBLIB_HU_SCL.ISCRIPT1.FieldFormula.IScript_SearchByReq?ACAD_CAREER=HCOL')).text();
  const doc = new DOMParser().parseFromString(res, 'text/html');
  const json = JSON.parse(doc.querySelector('.ptprtlcontainer')?.textContent as string);
  return json;
};
