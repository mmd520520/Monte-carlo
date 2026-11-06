function [remainingWeight, absorbedWeight] = Step7_Drop(weight, mua, segmentLength)
    % 第7步。输入权重、吸收系数和段长，输出剩余权重与沉积量。
    absorbedWeight = weight*(-expm1(-mua*segmentLength));
    remainingWeight = weight-absorbedWeight;
end
