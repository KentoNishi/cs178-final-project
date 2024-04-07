export const getCartInfo = async () => {
  const res = await (await fetch('https://portal.my.harvard.edu/psp/hrvihprd/EMPLOYEE/HRMS/s/WEBLIB_IS_DS.ISCRIPT1.FieldFormula.IScript_DrawSection?group=IS_SSS_SUMMARY_VIEW&section=SUMMARY_ALL')).text();
  const doc = new DOMParser().parseFromString(res, 'text/html');
  const terms = Array.from(doc.querySelectorAll('.isSSS_ShCtTermWrp:not(.huSSS_EnrollmentEvents)')).map(div => {
    const cartName = div.querySelector('h2')?.textContent as string;
    const cartClasses = Array.from(div.querySelectorAll('tr')).slice(1).map(tr => {
      const title = tr.querySelector('[headers="tblCart_Course"]')?.textContent as string;
      const session = tr.querySelector('[headers="tblCart_Session"]')?.textContent as string;
      const instructor = tr.querySelector('[headers="tblCart_Instructor"]')?.textContent as string;
      const location = tr.querySelector('[headers="tblCart_Location"]')?.textContent as string;
      const time = tr.querySelector('[headers="tblCart_Time"]')?.textContent as string;
      const day = tr.querySelector('[headers="tblCart_Day"]')?.textContent as string;
      return { title, session, instructor, location, time, day };
    }).filter(item => item.title);
    return { cartName, cartClasses };
  });
  // also do this for isSSS_ShCtSchTable
  return terms;
};
