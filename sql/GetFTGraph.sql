/*
Получить граф функциональные события (Function Event) - деревья отказов (Fault Tree)
*/
SELECT DISTINCT
FE.ID AS Node1,   --функциональное событие
FT.ID AS Node2,   --дерево отказов
'FE-FT' AS TYPE,   --тип связи
case Gates.Symbol
	when 100 then 'or'
	when 200 then 'and'
	when 300 then 'k/n'
	when 400 then 'nor'
end as Gate
FROM EVENTS AS FE
JOIN FEInputs ON FEInputs.FENum=FE.Num AND FEInputs.FEType=FE."Type"
JOIN EVENTS AS Gates ON Gates.Num = FEInputs.InputNum AND Gates.type = FEInputs.InputType
JOIN FTNodes ON FTNodes.RecNum = Gates.Num AND FTNodes.RecType = Gates.Type
JOIN FT ON FT.Num = FTNodes.FTNum
WHERE FE.Type = 11 AND Gates."Type"=6 AND FTNodes.FatherGateNum=0
UNION
/*
Получить граф дерево отказов (Fault Tree) - дерево отказов (Fault Tree)
*/
SELECT DISTINCT
FT.ID AS Node1,
rFT.ID AS Node2,
'FT-FT' AS TYPE,
case Gates.Symbol
	when 100 then 'or'
	when 200 then 'and'
	when 300 then 'k/n'
	when 400 then 'nor'
end as Gate
FROM FT	-- Верхнее дерево
JOIN FTNodes ON FTNodes.FTNum = FT.Num		-- Отцовские нодыНоды верзнего дерева, 
JOIN EVENTS AS Gates ON Gates.Num = FTNodes.RecNum AND Gates.Type = FTNodes.RecType		
JOIN FTNodes AS rFTNodes ON rFTNodes.RecNum = Gates.Num AND rFTNodes.RecType = Gates.Type
JOIN FT AS rFT ON rFT.Num = rFTNodes.FTNum
WHERE
rFTNodes.FatherGateNum = 0 AND rFTNodes.RecType != 21 AND rFTNodes.RecType = 6 AND
FTNodes.FatherGateNum != 0 AND FTNodes.Transfer = -1
ORDER BY TYPE, Node1, Node2