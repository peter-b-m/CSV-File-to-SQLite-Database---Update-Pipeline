drop view vw_birthdays_of_famous_people;

create view vw_birthdays_of_famous_people 
as 
select 
	 BDOFP.Name 
	,BDOFP.Date_Of_Birth 
	,ESS.European_Star_Sign 
	,CSS.Element 
	,CSS.Chinese_Star_Sign 
	,CSS.Yin_Yang 
	,CSS.Trine 
from 
	(
	select 
		 Name 
		,Date_Of_Birth 
		,substr(Date_Of_Birth, 1, 4) * 1 as Birth_Year 
		,substr(Date_Of_Birth, 6, 2) * 1 as Birth_Month 
		,substr(Date_Of_Birth, 9, 2) * 1 as Birth_Day 
	from 
		raw_birthdays_of_famous_people 
	) BDOFP 

		left join raw_chinese_star_signs CSS 
			on BDOFP.Date_Of_Birth between CSS.Start_Date and CSS.End_Date 

		left join 
			(
			select 
				 European_Star_Sign 
				,Start_Month 
				,Start_Day 
				,case
					when End_Month > Start_Month then End_Month 
					else Start_Month 
				end as End_Month 
				,case
					when End_Month > Start_Month then End_Day 
					else 31 
				end as End_Day 
			from 
				raw_european_star_signs 

			union all 
			
			select 
				 European_Star_Sign 
				,End_Month as Start_Month 
				,1 as Start_Day 
				,End_Month 
				,End_Day 
			from 
				raw_european_star_signs 
			where 
				End_Month < Start_Month 
			) ESS 
			on (BDOFP.Birth_Month = ESS.Start_Month and BDOFP.Birth_Day >= ESS.Start_Day)
			or (BDOFP.Birth_Month = ESS.End_Month and BDOFP.Birth_Day <= ESS.End_Day)
;

